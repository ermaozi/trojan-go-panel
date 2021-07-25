import os

from main.libs.task import jobs
"""
    警告:
        本文件内所有内容均属于敏感信息
        切勿将本文件以及本文件所在目录下的任何内容暴露在公开环境
        如果不慎泄露, 请立即停止服务, 并修改相关内容以避免损失

        使用前请先将本文件复制到当前目录, 并修改新文件名为 private.py
        private.py 在提交代码时不会被加入提交列表, 可放心修改
"""

__all__ = ["PriProduction", "PriDevelopment", "PriTesting"]


class Base(object):
    SECRET_KEY = 'flask_secret_key'  # 密钥, Flask 部分请求需要用到该密钥

    DOMAIN = os.getenv('DOMAIN')

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    JOBS = jobs


class PriProduction(Base):
    """
    生产环境配置
    使用 uWSGI 直接调用 app 时使用此环境
    """
    DIALECT = 'mysql'  # 数据库语法, 本项目使用 mariadb, 属于 mysql 语法
    DRIVER = 'pymysql'  # 数据库链接工具, 本项目使用 pymysql
    USERNAME = 'root'  # 数据库用户名, 默认 root
    PASSWORD = os.getenv('PRO-PASSWORD')  # 你的数据库密码
    HOST = os.getenv('DOMAIN')  # 数据库地址, 默认 127.0.0.1, 若使用其他服务器, 请填写该服务器的公网 ip
    PORT = '3306'  # 数据库端口, 默认 3306
    DATABASE = 'main'  # 数据库名称

    SQLALCHEMY_DATABASE_URI = f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}'\
                              f'@{HOST}:{PORT}/{DATABASE}?charset=utf8'


class PriTesting(Base):
    """
    测试环境配置
    使用单元测试时会使用此配置
    """
    DIALECT = 'mysql'  # 数据库语法, 本项目使用 mariadb, 属于 mysql 语法
    DRIVER = 'pymysql'  # 数据库链接工具, 本项目使用 pymysql
    USERNAME = 'root'  # 数据库用户名, 默认 root
    PASSWORD = 'TEST-PASSWORD'  # 你的数据库密码
    HOST = '127.0.0.1'  # 数据库地址, 默认 127.0.0.1, 若使用其他服务器, 请填写该服务器的公网 ip
    PORT = '3306'  # 数据库端口, 默认 3306
    DATABASE = 'main'  # 数据库名称

    SQLALCHEMY_DATABASE_URI = f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}'\
                              f'@{HOST}:{PORT}/{DATABASE}?charset=utf8'


class PriDevelopment(Base):
    """
    开发环境配置
    直接运行 manage.py 时会使用此配置
    """
    DIALECT = 'mysql'  # 数据库语法, 本项目使用 mariadb, 属于 mysql 语法
    DRIVER = 'pymysql'  # 数据库链接工具, 本项目使用 pymysql
    USERNAME = 'root'  # 数据库用户名, 默认 root
    PASSWORD = 'DEV-PASSWORD'  # 你的数据库密码
    HOST = '127.0.0.1'  # 数据库地址, 默认 127.0.0.1, 若使用其他服务器, 请填写该服务器的公网 ip
    PORT = '3306'  # 数据库端口, 默认 3306
    DATABASE = 'main'  # 数据库名称
    SQLALCHEMY_DATABASE_URI = f'{DIALECT}+{DRIVER}://{USERNAME}:{PASSWORD}'\
                              f'@{HOST}:{PORT}/{DATABASE}?charset=utf8'
