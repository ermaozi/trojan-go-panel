import string
import random
import psutil
import time
import os


"""
乱七八糟的小工具
"""


def Singleton(cls):
    """
    单例模式装饰器
    """
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


def bytes2human(n):
    """
    数据单位生成器
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return f'{value:.2f}{s}'
    return f"{n}B"


def get_node_status():
    """
    获取本机硬件状态
    """
    cpu_percent = psutil.cpu_percent(0)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    try:
        disk = os.statvfs("/")
        disk_used = disk.f_bsize * (disk.f_blocks - disk.f_bfree)
        disk_total = disk.f_blocks * disk.f_bsize
    except AttributeError as e:
        print("windows下开发, os.statvfs()会报错, 委曲求全, 出此下策", str(e))
        disk_used = 0
        disk_total = 1

    before = psutil.net_io_counters()
    time.sleep(1)
    now = psutil.net_io_counters()
    up_speed = now.bytes_sent - before.bytes_sent
    down_speed = now.bytes_recv - before.bytes_recv

    return {
        "cpu_percent": cpu_percent,
        "mem_percent": mem.percent,
        "mem_total": bytes2human(mem.total),
        "mem_used": bytes2human(mem.used),
        "swap_percent": swap.percent,
        "swap_total": bytes2human(swap.total),
        "swap_used": bytes2human(swap.used),
        "disk_percent": float(f"{disk_used/disk_total * 100:.2f}"),
        "disk_total": bytes2human(disk_total),
        "disk_used": bytes2human(disk_used),
        "up_speed": bytes2human(up_speed),
        "down_speed": bytes2human(down_speed)
    }


def create_random_str(nummin, nummax, chars=None):
    """
    随机字符串生成器
    """
    chars = chars or string.ascii_letters + string.digits
    return "".join(
        random.choice(chars) for _ in range(random.randint(nummin, nummax)))
