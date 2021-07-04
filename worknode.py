import psutil
from flask import Flask
import os
import time

app = Flask(__name__)


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


@app.route("/get_hw_info")
def hello_world():
    cpu_percent = psutil.cpu_percent(0)
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    disk = os.statvfs("/")

    disk_used = disk.f_bsize * (disk.f_blocks - disk.f_bfree)
    disk_total = disk.f_blocks * disk.f_bsize

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

