from datetime import datetime
from main.models.mode import User, NodeInfo, UserNods, db
from main.models.modetool import Database
from main.libs.local_db import DBApi


def check_user(user_api, user_node_api, username=None):
    """
    检查当前限制（日期/流量限制）
    若超过使用限制则将该用户所有链接可用流量置为0
    不传入 username 将会检查所有用户
    """
    if username:
        user_list = [user_api.get_user(username)]
    else:
        user_list = user_api.get_all_user()
    for user in user_list:
        username = user["username"]
        quota = user.get("quota")
        expiry_date = user.get("expiry_date")
        nodes = user_node_api.get_node_for_user_name(username)
        user_node_api.restore_user_traffic(username, nodes)
        if expiry_date and expiry_date < datetime.now():
            if expiry_date < datetime.now():
                user_node_api.limit_user_traffic(username, nodes)
        if quota > 0:
            total = user_api.get_user_use(username, nodes)
            if (quota * 1024 * 1024 * 1024) < total:
                user_node_api.limit_user_traffic(username, nodes)


def add_locol_trojan():
    """
    将主节点添加至可用节点
    """
    from main.libs.setting import setting
    if setting.get("trojan", "is_local_trojan"):
        db = Database(NodeInfo)
        data = {
            "node_name": "本机",
            "node_remarks": "本机节点",
            "node_domain": "localhost",
            "node_encryption_key": "null",
            "node_region": "无",
            "node_db": "local_trojan",
        }
        db.insert(data)


class UserTable(object):
    def __init__(self) -> None:
        self.db = Database(User)
        self.node_db_dict = NodeInfoTable().get_node_db_dict()

    def add_user(self, data):
        """
        添加用户
        """
        self.db.insert(data)

    def get_user(self, username):
        """
        获取单个用户的所有信息
        """
        return self.db.select({"username": username})[0]

    def set_user(self, username, user_data):
        """
        修改用户信息
        """
        self.db.update({"username": username}, user_data)

    def del_user(self, username):
        """
        删除单个用户
        """
        user_permission = self.db.select({"username": username},
                                         ["user_permission"])[0]
        print(user_permission)
        if user_permission["user_permission"] >= 100:
            return False, "创建人用户无法删除"
        self.db.delete({"username": username})
        return True, ""

    def verify_user(self, username, password):
        """
        检查用户与密码是否匹配
        每次检查都会更新用户表中的login_time
        每次检查失败, 用户表中num_of_fail会+1
        若num_of_fail>= 5, 检查失败后需要等待300
        """
        fucking_time = 300
        fucking_numb = 5
        usr = db.session.query(User).filter_by(username=username).first()
        if usr:
            sleep_time = fucking_time - (datetime.now() - usr.login_time).seconds
            if usr.num_of_fail >= fucking_numb and sleep_time > 0:
                m ,s = divmod(sleep_time, 60)
                return False, f"账户已被锁定, 请在{m}分{s}秒后重新尝试"
            is_ok = usr.check_password(password)
            if is_ok:
                self.db.update({"username": username},
                               {"num_of_fail": 0,
                                "login_time": datetime.now()})
                return usr.check_password(password), usr.username
            else:
                cur_num_of_fail = usr.num_of_fail + 1 if usr.num_of_fail < fucking_numb else usr.num_of_fail
                self.db.update({"username": username},
                               {"num_of_fail": cur_num_of_fail,
                                "login_time": datetime.now()})
                if cur_num_of_fail >= fucking_numb:
                    return False, f"密码错误, 账号已被锁定, {fucking_time//60} 分钟后再来吧"
                return False, f"密码错误, 失败{fucking_numb-cur_num_of_fail}次后账号将被锁定 {fucking_time//60} 分钟"
        else:
            return False, "用户不存在"

    def get_user_permission(self, username):
        """
        获取用户权限等级
        """
        return self.db.select({"username": username},
                              ["user_permission"])[0]["user_permission"]

    def get_all_user(self):
        """
        获取所有用户的所有信息
        """
        return(self.db.select())

    def username_if_exist(self, username):
        """
        检查用户是否存在, 已存在返回 True, 不存在返回 False
        """
        return bool(self.db.select({"username": username}))

    def get_user_use(self, username, node_list):
        """
        获取用户流量使用情况
        分别为: 上传流量, 下载流量, 总流量
        单位为 B
        """
        upload = download = 0
        sql = f'select download,upload from users where username="{username}"'
        for node in node_list:
            with DBApi(self.node_db_dict[node]) as db:
                db.cur.execute(sql)  # 执行sql语句
                results = db.cur.fetchall()
                if results:
                    download += results[0][0]
                    upload += results[0][1]
        return upload, download, download + upload


class UserNodesTable(object):
    def __init__(self) -> None:
        self.db = Database(UserNods)
        self.node_db_dict = NodeInfoTable().get_node_db_dict()

    def get_node_for_user_name(self, user_name):
        """
        获取用户名对应的所有节点名
        """
        nodes = self.db.select({"user_name": user_name}, ["node_name"])
        return [i["node_name"] for i in nodes]

    def get_node_info_for_user_name(self, user_name):
        """
        获取用户名对应的所有节点信息
        """
        return self.db.select({"user_name": user_name})

    def get_username_for_nodename(self, node_name):
        """
        获取节点名对应的所有用户名
        """
        nodes = self.db.select({"node_name": node_name}, ["user_name"])
        return [i["user_name"] for i in nodes]

    def add_user_node(self, data_list):
        """
        向某用户添加一个或多个节点
        """
        for data in data_list:
            node_name = data["node_name"]
            user_name = data["user_name"]
            pwd = data["node_pwd"]
            with DBApi(self.node_db_dict[node_name]) as db:
                db.insert_user(user_name, pwd)
        self.db.insert_list(UserNods, data_list)

    def del_user_node(self, data_list):
        """
        删除某用户的一个或多个节点
        """
        for data in data_list:
            node_name = data["node_name"]
            user_name = data["user_name"]
            with DBApi(self.node_db_dict[node_name]) as db:
                sql = f'delete from users where username="{user_name}";'
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()
            self.db.delete(data)

    def del_user(self, username):
        """
        通过用户名删除所有匹配到的记录
        """
        self.db.delete({"user_name": username})

    def del_node(self, node_name):
        """
        通过节点名删除所有匹配到的记录
        """
        self.db.delete({"node_name": node_name})

    def limit_user_traffic(self, user_name, nodes):
        """
        将某用户名下所有的节点置为【不可用】(可用流量置为0)
        """
        sql = f'UPDATE users SET quota=0 where username="{user_name}";'
        for node_name in nodes:
            with DBApi(self.node_db_dict[node_name]) as db:
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()

    def restore_user_traffic(self, user_name, nodes):
        """
        将某用户名下所有的节点置为【可用】(可用流量置为-1)
        """
        sql = f'UPDATE users SET quota=-1 where username="{user_name}";'
        for node_name in nodes:
            with DBApi(self.node_db_dict[node_name]) as db:
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()


class NodeInfoTable(object):
    def __init__(self) -> None:
        self.db = Database(NodeInfo)

    def get_node_db_dict(self):
        """
        获取node_name对应的node_db
        """
        node_db_dict = {}
        for node in self.db.select():
            node_db_dict[node["node_name"]] = node["node_db"]
        return node_db_dict

    def add_node(self, data):
        """
        添加节点, 并创建节点对应的数据库
        """
        if not data.get("node_db"):
            data["node_db"] = data["node_name"]  # 临时先用这个
        if data.get("node_domain") == "local_host":
            data["node_db"] = "local_trojan"

        node_list = self.db.select({}, ["node_name", "node_domain"])
        node_name_list = [node.get("node_name") for node in node_list]
        node_domain_list = [node.get("node_domain") for node in node_list]
        if data["node_name"] in node_name_list:
            return False, f'节点名称{data["node_name"]}已存在!'
        if data["node_domain"] in node_domain_list:
            return False, f'域名{data["node_domain"]}已存在!'
        self.db.insert(data)

        with DBApi() as db:
            sql = f'create database {data["node_db"]}'
            db.cur.execute(sql)
        with DBApi(data["node_db"]) as db:
            sql = """CREATE TABLE users (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                    username VARCHAR(64) NOT NULL,
                    password CHAR(56) NOT NULL,
                    quota BIGINT NOT NULL DEFAULT 0,
                    download BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    upload BIGINT UNSIGNED NOT NULL DEFAULT 0,
                    PRIMARY KEY (id),
                    INDEX (password)
                );
                """
            db.cur.execute(sql)
        return True, ""

    def del_node(self, node_name):
        """
        删除节点, 并删除对应的数据库
        """
        node = self.db.select({"node_name": node_name})[0]
        with DBApi() as db:
            sql = f'drop database {node["node_db"]}'
            db.cur.execute(sql)
        self.db.delete({"node_name": node_name})

    def get_all_node_list(self):
        """
        获取所有的节点信息
        """
        select_list = ["node_name", "node_domain",
                       "node_region", "node_usernumber"]
        return self.db.select({}, select_list)

    def get_node_for_nodename(self, node_name):
        """
        通过节点名称获取节点信息
        """
        return self.db.select({"node_name": node_name})[0]

    def set_node_usernumber(self, node_name, usernumber):
        """
        修改节点中正在使用的用户数量
        """
        self.db.update({"node_name": node_name},
                       {"node_usernumber": usernumber})
