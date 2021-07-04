import os
import sys

sys.path.append(os.path.realpath(__file__ + "/../.."))

from flask.app import Flask
import random
import string
import unittest
from main.models.exts import db, bcrypt
from main.models.modetool import *
from main.models.mode import *
from main.libs.db_api import *

config = 'conf.flask.config.DevelopmentConfig'

app = Flask(__name__)

app.config.from_object(config)

db.init_app(app)
bcrypt.init_app(app)


def random_str(num, userstr=""):
    str_pool = userstr if userstr else string.ascii_letters + string.digits
    if len(str_pool) < num:
        str_pool *= num // len(str_pool) + 1
    return ''.join(random.sample(str_pool, num))


class TestModeTools(unittest.TestCase):
    def test_001_create_db(self):
        with app.app_context():
            creat_db()

    def test_002_modeapi(self):
        with app.app_context():
            user_api = Database(User)
            username = f"{random_str(10, string.digits)}"
            user_data = {
                "password": "test_pwd",
                "username": username
            }
            user_api.insert(user_data)

            # 检查密码
            self.assertTrue(user_api.check_password_for_name(
                username, "test_pwd"))
            self.assertFalse(
                user_api.check_password_for_name(username, "test_pwd_123"))

            # 查询空字典
            data = user_api.select()
            self.assertTrue(data)


            # 删除
            # data = user_api.select(condition, result)
            # domainname = data["domainname"]
            # user_api.delete(condition)

            # data = user_api.select(condition, result)
            # self.assertFalse(data)


class TestTabal(unittest.TestCase):
    def test_001_user(self):
        pass
    def test_002_node_info(self):
        node_api = NodeInfoTable()
        domain = "test01.ermao.net"
        node_data = {
            "node_name": "甲骨文测试01",
            "node_domain": domain,
            "node_encryption_key": f"{random_str(10, string.digits)}",
            "node_region": "日本东京",
            "node_db": "test01"
        }
        with app.app_context():
            node_api.add_node(**node_data)
            node_list = node_api.get_all_node_list()
            self.assertTrue(domain in node_list)

            node_api.del_node(domain)
            node_list = node_api.get_all_node_list()
            self.assertFalse(domain in node_list)




if __name__ == '__main__':
    unittest.main()
