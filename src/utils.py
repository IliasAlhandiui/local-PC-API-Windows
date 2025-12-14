import psutil
import time

# Keep previous net counters to compute rates
_last_net = {"t": None, "bytes_sent": None, "bytes_recv": None}


def disk_info(path: str):
    du = psutil.disk_usage(path)
    return {
        "mount": path,
        "percent": round(du.percent, 1),
        "free_gb": bytes_to_gb(du.free),
        "total_gb": bytes_to_gb(du.total),
    }


def bytes_to_gb(b: int) -> float:
    return round(b / (1024**3), 2)


def net_rates_kbps():
    global _last_net
    now = time.time()
    c = psutil.net_io_counters()
    if _last_net["t"] is None:
        _last_net = {"t": now, "bytes_sent": c.bytes_sent, "bytes_recv": c.bytes_recv}
        return 0.0, 0.0

    dt = max(now - _last_net["t"], 1e-6)
    up_kbps = (c.bytes_sent - _last_net["bytes_sent"]) / dt / 1024.0
    down_kbps = (c.bytes_recv - _last_net["bytes_recv"]) / dt / 1024.0

    _last_net = {"t": now, "bytes_sent": c.bytes_sent, "bytes_recv": c.bytes_recv}
    return round(down_kbps, 1), round(up_kbps, 1)


def top_processes(limit=5):
    # First call to prime cpu_percent measurement
    for p in psutil.process_iter(["pid"]):
        try:
            p.cpu_percent(None)
        except Exception:
            pass

    time.sleep(0.15)

    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append(
                {
                    "pid": info.get("pid"),
                    "name": (info.get("name") or "")[:40],
                    "cpu": float(info.get("cpu_percent") or 0.0),
                    "mem": float(info.get("memory_percent") or 0.0),
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    top_cpu = sorted(procs, key=lambda x: x["cpu"], reverse=True)[:limit]
    top_mem = sorted(procs, key=lambda x: x["mem"], reverse=True)[:limit]
    return top_cpu, top_mem
