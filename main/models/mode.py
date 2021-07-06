from main.models.exts import db
from main.models.exts import bcrypt

import datetime


class User(db.Model):
    __tablename__ = 'user'
    username = db.Column(db.String(80), primary_key=True)
    _password_hash_ = db.Column(db.String(255))
    quota = db.Column(db.INTEGER, default=-1)
    expiry_date = db.Column(db.DateTime, default=None)
    user_create_time = db.Column(db.DateTime, default=datetime.datetime.now())
    user_permission = db.Column(db.INTEGER, default=0)
    subscribe_pwd = db.Column(db.String(255), default="")
    num_of_fail = db.Column(db.INTEGER, default=0)
    login_time = db.Column(db.DateTime, default=datetime.datetime.now())

    @property
    def password(self):
        raise Exception('密码不能被读取')

    # 赋值password，则自动加密存储。
    @password.setter
    def password(self, value):
        self._password_hash_ = bcrypt.generate_password_hash(value)

    # 使用check_password,进行密码校验，返回True False。
    def check_password(self, pasword):
        return bcrypt.check_password_hash(self._password_hash_, pasword)


class NodeInfo(db.Model):
    __tablename__ = 'node_info'
    node_name = db.Column(db.String(255), primary_key=True)
    node_domain = db.Column(db.String(255))
    node_encryption_key = db.Column(db.String(255))
    node_region = db.Column(db.String(255))
    node_usernumber = db.Column(db.INTEGER, default=0)
    node_db = db.Column(db.String(255))
    required_permissions = db.Column(db.INTEGER, default=1)


class UserNods(db.Model):
    __tablename__ = 'user_node'
    id = db.Column(db.INTEGER, primary_key=True)
    user_name = db.Column(db.String(80))
    node_name = db.Column(db.String(255))
    node_pwd = db.Column(db.String(255))
