from flask import request, jsonify
from flask.views import MethodView
from main.libs.db_api import NodeInfoTable
from main.libs.threading_api import ThreadApi
from main.libs.auth_api import login_required, constant
import requests
import uuid
import json


__all__ = ["AddNode", "GetNodeStatus", "GetNodeStatus"]


data_dict = {}


class AddNode(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def post(self):
        node_api = NodeInfoTable()
        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        data["node_encryption_key"] = str(
            uuid.uuid5(uuid.NAMESPACE_DNS, data.get("node_name")))
        ret, msg = node_api.add_node(**data)

        if ret:
            return jsonify({'code': 200, 'data': ""})
        else:
            return jsonify({'code': 500, 'data': msg})


class GetNodeInfo(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def get(self):
        node_api = NodeInfoTable()
        node_list = node_api.get_all_node_list()
        data = {}
        data['node_list'] = node_list
        data['domain_list'] = [node.get("node_domain") for node in node_list]
        return jsonify({'code': 200, 'data': data})


class GetNodeStatus(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def post(self):
        datas = request.get_data()
        datas = json.loads(datas.decode("UTF-8"))
        thread_list = []
        for i in datas:
            domain = i["node_domain"]
            thread_list.append(ThreadApi(get_node_info, domain))
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()
        return jsonify({'code': 200, 'data': data_dict})


def get_node_info(domain):
    data = {}
    data["node_status"] = {}
    try:
        hw_info = requests.get(f'http://{domain}/get_hw_info')
        if hw_info.status_code == 200:
            data["node_status"]["status"] = "success"
            data["node_status"]["info"] = "正常"
            data["node_status"]["msg"] = "正常"
            data.update(json.loads(hw_info.text))
        else:
            data["node_status"]["status"] = "error"
            data["node_status"]["info"] = "异常"
            data["node_status"]["msg"] = "节点连接异常"
    except Exception as e:
        data["node_status"]["status"] = "error"
        data["node_status"]["info"] = "异常"
        data["node_status"]["msg"] = str(e)
    data_dict[domain] = data
