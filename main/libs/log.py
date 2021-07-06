import os
import time

"""
因为项目不需要什么运行日志, 所以决定自己写个简单的日志模块
"""

def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class Logs(object):
    def __init__(self):
        self.log_root_dir = "/var/log/trojan-go-panel/"

    def __log(self, util_name, level, message):
        log_dir = os.path.realpath(f"{self.log_root_dir}/{util_name}/")
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
        now_time = time.strftime("%Y-%m-%d.log %H:%M:%S", time.localtime())
        log_name, log_time = now_time.split(" ")
        log_time = time.strftime("%H:%M:%S", time.localtime())
        log_message = f"[{log_time}][{level}] - {message}\n"
        with open(os.path.join(log_dir, log_name), "a") as f:
            f.write(log_message.decode("utf-8"))

    def info(self, util_name, message):
        self.__log(util_name, "INFO", message)

    def debug(self, util_name, message):
        self.__log(util_name, "DEBUG", message)

    def warning(self, util_name, message):
        self.__log(util_name, "WARNING", message)

    def error(self, util_name, message):
        self.__log(util_name, "ERROR", message)


log = Logs()