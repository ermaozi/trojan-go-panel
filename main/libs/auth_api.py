# 在上面的基础上导入
import functools

from flask import current_app, jsonify, request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from main.libs.db_api import UserTable
from main.libs.constant import constant


# 权限等级, 数字越高权限越大
constant.PERMISSION_LEVEL_100 = 100  # 创建人
constant.PERMISSION_LEVEL_5 = 5  # 总代理
constant.PERMISSION_LEVEL_4 = 4  # 超级管理员
constant.PERMISSION_LEVEL_3 = 3  # 管理员
constant.PERMISSION_LEVEL_2 = 2  # 特权用户
constant.PERMISSION_LEVEL_1 = 1  # 普通用户
constant.PERMISSION_LEVEL_0 = 0  # 黑户


def login_required(level=constant.PERMISSION_LEVEL_5):
    def verify(view_func):
        @functools.wraps(view_func)
        def verify_token(*args, **kwargs):
            try:
                # 在请求头上拿到token
                token = request.headers["Authorization"]
            except Exception:
                # 没接收的到token,给前端抛出错误
                return jsonify(code=4103, msg='账号未登录')

            s = Serializer(current_app.config["SECRET_KEY"])
            try:
                user_api = UserTable()
                username = s.loads(token)["username"]
                user_permission = user_api.get_user_permission(username)
                if user_permission < level:
                    return jsonify(code=401, msg="权限不足")
            except Exception:
                return jsonify(code=401, msg="登录已过期")

            return view_func(*args, **kwargs)

        return verify_token
    return verify


def create_token(data):
    s = Serializer(current_app.config["SECRET_KEY"], expires_in=3600)
    token = s.dumps(data).decode("ascii")
    return token


# def verify_token(token):
#     # 参数为私有秘钥，跟上面方法的秘钥保持一致
#     s = Serializer(current_app.config["SECRET_KEY"])
#     try:
#         # 转换为字典
#         data = s.loads(token)
#         print(data)
#     except Exception:
#         return None
#     return data
