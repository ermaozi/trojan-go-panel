import base64
import json
import random
import string
import datetime


from flask import Response, jsonify, request, render_template
from flask.views import MethodView
from main.libs.auth_api import create_token, login_required, constant
from main.libs.db_api import NodeInfoTable, UserNodesTable, UserTable
from main.libs.log import log

__all__ = [
    "Login", "Logout", "User", "GetTrojanUrl", "Subscribe"
]


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f'{value:.2f}{s}'
    return f"{n}B"


def create_random_str(nummin, nummax):
    chars = string.ascii_letters + string.digits
    return "".join(
        random.choice(chars) for _ in range(random.randint(nummin, nummax)))


def check_user(username):
    user_api = UserTable()
    user_node_api = UserNodesTable()

    user_data = user_api.get_user(username)
    username = user_data["username"]
    quota = user_data.get("quota")
    expiry_date = user_data.get("expiry_date")
    nodes = user_node_api.get_node_for_user_name(username)
    user_node_api.restore_user_traffic(username, nodes)
    if expiry_date and expiry_date < datetime.datetime.now():
        if expiry_date < datetime.datetime.now():
            user_node_api.limit_user_traffic(username, nodes)
    if quota > 0:
        total = user_api.get_user_use(username, nodes)
        if (quota * 1024 * 1024 * 1024) < total:
            user_node_api.limit_user_traffic(username, nodes)


class Login(MethodView):
    def post(self):
        user_api = UserTable()
        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        username = data.get('username')
        password = data.get('password')

        check_result, msg = user_api.verify_user(username, password)

        log.info("user", f"{username} 尝试登录 使用ip:{request.remote_addr}")

        if check_result:
            ret = {
                'code': 200,
                'data': {
                    'token': create_token({"username": username}),
                    'username': username
                }
            }
            log.info("user", f"{username} 登录成功 使用ip:{request.remote_addr}")
        else:
            ret = {
                'code': 401,
                'message': msg
            }
            log.info("user", f"{username} 登录失败:'{msg}' 使用ip:{request.remote_addr}")
        return jsonify(ret)

    def get(self):
        return render_template("index.html")


class Logout(MethodView):
    def post(self):
        pass


class User(MethodView):
    def post(self):
        user_api = UserTable()
        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        try:
            username = data.get("username")
            if user_api.username_if_exist(username):
                raise Exception("用户名重复, 请重新输入")
            user_data = data
            if not user_api.get_all_user():
                # 首个账号默认为创建人
                user_data["user_permission"] = constant.PERMISSION_LEVEL_100
            subscribe_pwd = create_random_str(8, 16)
            user_data["subscribe_pwd"] = subscribe_pwd
            user_api.add_user(user_data)
            log.info("user", f"{username} 成功注册用户")
            return jsonify({'code': 200, 'data': {}})
        except Exception as err:
            log.error("user", f"{username} 注册失败{str(err)}{user_data}")
            return jsonify({'code': 400, 'message': str(err)})

    @login_required(constant.PERMISSION_LEVEL_4)
    def get(self):
        user_api = UserTable()
        user_node_api = UserNodesTable()
        node_api = NodeInfoTable()

        data_list = []
        for i in user_api.get_all_user():
            data = {}
            username = i["username"]
            quota = i.get("quota")
            expiry_date = i.get("expiry_date")
            data["username"] = username
            data["user_permission"] = i.get("user_permission")
            data["quota"] = "无限制" if quota == -1 else quota
            data["expiry_date"] = expiry_date.strftime(
                '%Y-%m-%d') if expiry_date else "永久"
            data["nodes"] = user_node_api.get_node_for_user_name(username)

            upload, download, total = user_api.get_user_use(
                username, data["nodes"])
            data["upload"] = bytes2human(upload)
            data["download"] = bytes2human(download)
            data["total"] = bytes2human(total)

            data_list.append(data)
        node_list = [
            node["node_name"] for node in node_api.get_all_node_list()
        ]

        ret = {
            "code": 200,
            "data": {
                "user_list": data_list,
                "node_list": node_list
            }
        }
        return jsonify(ret)

    @login_required(constant.PERMISSION_LEVEL_4)
    def put(self):
        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        user_name = data["username"]
        user_data = data["user_data"]
        node_list = data["node_list"]
        user_api = UserTable()
        user_node_api = UserNodesTable()
        node_api = NodeInfoTable()

        if not user_api.username_if_exist(user_name):
            return jsonify({
                "code": 200,
                "data": {
                    "msg": f"用户名{user_name}不存在!"
                }
            })
        if not user_data.get("expiry_date"):
            user_data["expiry_date"] = None
        if user_data.get("quota") == "无限制":
            user_data["quota"] = -1
        user_api.set_user(user_name, user_data)

        exist_node_set = set(user_node_api.get_node_for_user_name(user_name))
        all_node_set = set(
            [i["node_name"] for i in node_api.get_all_node_list()])
        node_set = set(node_list)
        available_node_set = all_node_set - exist_node_set
        insert_list = list(available_node_set & node_set)
        del_list = list(exist_node_set - node_set)

        insert_data_list = [{
            "user_name": user_name,
            "node_name": node,
            "node_pwd": create_random_str(8, 16)
        } for node in insert_list]
        user_node_api.add_user_node(insert_data_list)

        del_data_list = [{
            "user_name": user_name,
            "node_name": node
        } for node in del_list]
        user_node_api.del_user_node(del_data_list)

        all_set_node = del_data_list+insert_data_list

        for node in all_set_node:
            node_name = node["node_name"]
            node_usernumber = len(user_node_api.get_username_for_nodename(node_name))
            node_api.set_node_usernumber(node_name, node_usernumber)
        if all_set_node:
            check_user(user_name)

        return jsonify({"code": 200, "data": {}})


class DelUser(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def post(self):

        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        user_name = data["username"]
        user_api = UserTable()
        user_api.del_user(user_name)
        user_node_api = UserNodesTable()
        user_node_api.del_user(user_name)
        del_list = user_node_api.get_node_for_user_name(user_name)
        del_data_list = [{
            "user_name": user_name,
            "node_name": node
        } for node in del_list]
        user_node_api.del_user_node(del_data_list)
        return jsonify({"code": 200, "data": {}})


class GetTrojanUrl(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def get(self):
        user_name = request.args["0"]

        user_api = UserTable()
        user_node_api = UserNodesTable()
        node_api = NodeInfoTable()

        trojan_urls = []

        node_info_list = user_node_api.get_node_info_for_user_name(user_name)
        for node_info in node_info_list:
            pwd = node_info["node_pwd"]
            node_name = node_info["node_name"]
            node = node_api.get_node_for_nodename(node_name)
            node_domain = node["node_domain"]
            node_region = node["node_region"]
            trojan_urls.append(f"trojan://{pwd}@{node_domain}:443#{node_region}|{node_name}")
        subscribe_pwd = user_api.get_user(user_name)["subscribe_pwd"]
        subscribe_link = ""
        if subscribe_pwd:
            subscribe_link = f"/user/subscribe?u={user_name}&p={subscribe_pwd}"
        data = {}
        data["trojan_urls"] = trojan_urls
        data["subscribe_link"] = subscribe_link
        return jsonify({"code": 200, "data": data})


class Subscribe(MethodView):
    @login_required(constant.PERMISSION_LEVEL_4)
    def post(self):
        data = request.get_data()
        data = json.loads(data.decode("UTF-8"))
        user_name = data["username"]

        user_api = UserTable()
        subscribe_pwd = create_random_str(8, 16)
        user_api.set_user(user_name, {"subscribe_pwd": subscribe_pwd})
        return jsonify({"code": 200, "data": {}})

    def generating_fake_data(self):
        # ᕕ( ᐛ )ᕗ 如果密码不对, 就返回随机假数据
        trojan_urls = []
        for _ in range(random.randint(1, 20)):
            domain3 = create_random_str(5, 9)
            domain2 = create_random_str(3, 5)
            domain1 = random.choice(["com", "net", "org", "xyz", "cc", "fuck", "io"])
            pwd = create_random_str(5, 9)
            trojan_urls.append(f"trojan://{pwd}@{domain3}.{domain2}.{domain1}:443")
        nodes_str = "\n".join(trojan_urls)
        return base64.b64encode(nodes_str.encode("utf-8"))

    def get(self):
        rsp = dict(request.args)
        user_name = rsp["u"]
        subscribe_pwd = rsp["p"]

        user_api = UserTable()
        user_node_api = UserNodesTable()
        node_api = NodeInfoTable()

        content = ""

        if not user_api.username_if_exist(user_name):
            content = self.generating_fake_data()
            response = Response(content, content_type="text/plain;charset=utf-8")
            return response

        v_subscribe_pwd = user_api.get_user(user_name)["subscribe_pwd"]

        if subscribe_pwd != v_subscribe_pwd:
            content = self.generating_fake_data()
            response = Response(content, content_type="text/plain;charset=utf-8")
            return response

        try:
            trojan_urls = []
            node_info_list = user_node_api.get_node_info_for_user_name(
                user_name)
            for node_info in node_info_list:
                pwd = node_info["node_pwd"]
                node_name = node_info["node_name"]
                node = node_api.get_node_for_nodename(node_name)
                node_domain = node["node_domain"]
                node_region = node["node_region"]
                trojan_urls.append(f"trojan://{pwd}@{node_domain}:443#{node_region}|{node_name}")
            nodes_str = "\n".join(trojan_urls)
            content = base64.b64encode(nodes_str.encode("utf-8"))
        except Exception as e:
            return "错误"

        response = Response(content, content_type="text/plain;charset=utf-8")
        return response
