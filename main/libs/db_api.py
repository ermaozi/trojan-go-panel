from datetime import datetime
from main.models.mode import User, NodeInfo, UserNods, db
from main.models.modetool import Database
from main.libs.local_db import DBApi


class UserTable(object):
    def __init__(self) -> None:
        self.db = Database(User)

    def add_user(self, username, password, subscribe_pwd="", user_permission=0):
        db_data = {
            "username": username,
            "password": password,
            "user_permission": user_permission,
            "subscribe_pwd": subscribe_pwd
        }
        self.db.insert(db_data)

    def get_user(self, username):
        return self.db.select({"username": username})[0]

    def set_user(self, username, user_data):
        self.db.update({"username": username}, user_data)

    def del_user(self, username):
        self.db.delete({"username": username})

    def verify_user(self, username, password):
        fucking_time = 10
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
        return self.db.select({"username": username},
                              ["user_permission"])[0]["user_permission"]

    def get_all_user(self):
        return(self.db.select())

    def username_if_exist(self, username):
        return bool(self.db.select({"username": username}))

    def get_user_use(self, username, node_list):
        upload = download = 0
        sql = f'select download,upload from users where username="{username}"'
        for node in node_list:
            with DBApi(node) as db:
                db.cur.execute(sql)  # 执行sql语句
                results = db.cur.fetchall()
                if results:
                    download += results[0][0]
                    upload += results[0][1]
        return upload, download, download + upload


class UserNodesTable(object):
    def __init__(self) -> None:
        self.db = Database(UserNods)

    def get_node_for_user_name(self, user_name):
        nodes = self.db.select({"user_name": user_name}, ["node_name"])
        return [i["node_name"] for i in nodes]

    def get_node_info_for_user_name(self, user_name):
        return self.db.select({"user_name": user_name})

    def get_username_for_nodename(self, node_name):
        nodes = self.db.select({"node_name": node_name}, ["user_name"])
        return [i["user_name"] for i in nodes]

    def add_user_node(self, data_list):
        for data in data_list:
            node_name = data["node_name"]
            user_name = data["user_name"]
            pwd = data["node_pwd"]
            with DBApi(node_name) as db:
                db.insert_user(user_name, pwd)
        self.db.insert_list(UserNods, data_list)

    def del_user_node(self, data_list):
        for data in data_list:
            node_name = data["node_name"]
            user_name = data["user_name"]
            with DBApi(node_name) as db:
                sql = f'delete from users where username="{user_name}";'
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()
            self.db.delete(data)

    def del_user(self, username):
        self.db.delete({"user_name": username})

    def del_node(self, node_name):
        self.db.delete({"node_name": node_name})

    def limit_user_traffic(self, user_name, nodes):
        sql = f'UPDATE users SET quota=0 where username="{user_name}";'
        print(sql)
        for node_name in nodes:
            with DBApi(node_name) as db:
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()

    def restore_user_traffic(self, user_name, nodes):
        sql = f'UPDATE users SET quota=-1 where username="{user_name}";'
        for node_name in nodes:
            with DBApi(node_name) as db:
                db.cur.execute(sql)  # 执行sql语句
                db.db.commit()


class NodeInfoTable(object):
    def __init__(self) -> None:
        self.db = Database(NodeInfo)

    def add_node(self, node_name, node_domain, node_encryption_key,
                 node_region):
        db_data = {
            "node_name": node_name,
            "node_domain": node_domain,
            "node_encryption_key": node_encryption_key,
            "node_region": node_region,
            "node_db": node_name
        }
        node_list = self.db.select({}, ["node_name", "node_domain"])
        node_name_list = [node.get("node_name") for node in node_list]
        node_domain_list = [node.get("node_domain") for node in node_list]
        if node_name in node_name_list:
            return False, f"节点名称{node_name}已存在!"
        if node_domain in node_domain_list:
            return False, f"域名{node_domain}已存在!"
        self.db.insert(db_data)

        with DBApi() as db:
            sql = f"create database {node_name}"
            db.cur.execute(sql)
        with DBApi(node_name) as db:
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

    def del_node(self, node_domain):
        self.db.delete({"node_domain": node_domain})

    def get_all_node_list(self):
        return self.db.select({},
            ["node_name", "node_domain", "node_region", "node_usernumber"])

    def get_node_for_nodename(self, node_name):
        return self.db.select({"node_name": node_name})[0]

    def set_node_usernumber(self, node_name, usernumber):
        self.db.update({"node_name": node_name},
                       {"node_usernumber": usernumber})