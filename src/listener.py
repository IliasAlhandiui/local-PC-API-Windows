from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
from utils import bytes_to_gb, net_rates_kbps, top_processes, disk_info
import os
import psutil
import socket
import platform
import time

app = Flask(__name__)
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


# --------------- Flask App Routes -----------#
@app.get("/")
def root():
    return "OK"


@app.route("/shutdown", methods=["GET"])
def shutdown():
    if request.args.get("token") != ACCESS_TOKEN:
        return "Unauthorized", 401
    os.system("shutdown /h /t 1")
    return "OK"


@app.route("/restart", methods=["GET"])
def restart():
    if request.args.get("token") != ACCESS_TOKEN:
        return "Unauthorized", 401
    os.system("shutdown /r /t 1")
    return "OK"


@app.route("/sleep", methods=["GET"])
def sleep():
    if request.args.get("token") != ACCESS_TOKEN:
        return "Unauthorized", 401
    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    return "OK"


@app.get("/status")
def status_page():
    if request.args.get("token") != ACCESS_TOKEN:
        return "Unauthorized", 401

    return render_template("Status.html")


@app.get("/status.json")
def status_json():
    if request.args.get("token") != ACCESS_TOKEN:
        return "Unauthorized", 401

    boot = psutil.boot_time()
    vm = psutil.virtual_memory()

    down_kbps, up_kbps = net_rates_kbps()
    cpu_total = psutil.cpu_percent(interval=0.1)
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

    top_cpu, top_mem = top_processes(limit=5)

    disks = [
        disk_info("C:\\"),
        disk_info("D:\\"),
        disk_info("E:\\"),
    ]

    alerts = []
    # low disk warning if ANY drive is high usage
    for d in disks:
        if d["percent"] >= 85:
            alerts.append(f"LOW_DISK_{d['mount'][0]}")
    if vm.percent >= 90:
        alerts.append("HIGH_RAM")
    if cpu_total >= 90:
        alerts.append("HIGH_CPU")

    return jsonify(
        {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "uptime_sec": int(time.time() - boot),
            "cpu": {
                "total_percent": round(cpu_total, 1),
                "per_core_percent": [round(x, 1) for x in cpu_per_core],
            },
            "ram": {
                "percent": round(vm.percent, 1),
                "used_gb": bytes_to_gb(vm.used),
                "available_gb": bytes_to_gb(vm.available),
                "total_gb": bytes_to_gb(vm.total),
            },
            "disks": disks,
            "network": {
                "down_kbps": down_kbps,
                "up_kbps": up_kbps,
            },
            "top_processes": {
                "cpu": top_cpu,
                "ram": top_mem,
            },
            "alerts": alerts,
            "ts": int(time.time()),
        }
    )



app.run(host="0.0.0.0", port=5000)
