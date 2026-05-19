"""
系统监控服务模块 - 获取服务器CPU/内存/磁盘使用率
适配阿里云ECS 2核2G环境，轻量级实现
"""

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import psutil


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    cpu_percent: float          # CPU使用率(%)
    memory_percent: float       # 内存使用率(%)
    memory_used_mb: float       # 已用内存(MB)
    memory_total_mb: float      # 总内存(MB)
    disk_percent: float         # 磁盘使用率(%)
    disk_used_gb: float         # 已用磁盘(GB)
    disk_total_gb: float        # 总磁盘(GB)
    timestamp: datetime         # 采集时间


def get_cpu_usage(interval: float = 0.5) -> float:
    """
    获取CPU使用率

    Args:
        interval: 采样间隔（秒），psutil需要至少0.1秒才能获取有意义的值

    Returns:
        float: CPU使用率百分比（0-100）
    """
    return psutil.cpu_percent(interval=interval)


def get_memory_usage() -> dict[str, float]:
    """
    获取内存使用情况

    Returns:
        dict: 包含percent/used_mb/total_mb的字典
    """
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used_mb": round(mem.used / (1024 * 1024), 2),
        "total_mb": round(mem.total / (1024 * 1024), 2),
    }


def get_disk_usage(path: str = "/") -> dict[str, float]:
    """
    获取磁盘使用情况

    Args:
        path: 要检查的磁盘路径，默认根目录

    Returns:
        dict: 包含percent/used_gb/total_gb的字典
    """
    disk = psutil.disk_usage(path)
    return {
        "percent": disk.percent,
        "used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
        "total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
    }


def get_system_metrics() -> SystemMetrics:
    """
    获取完整的系统指标
    一次性采集所有指标，减少多次调用开销

    Returns:
        SystemMetrics: 系统指标数据对象
    """
    # CPU采样（需要短暂间隔）
    cpu_percent = get_cpu_usage(interval=0.3)

    # 内存
    mem_info = get_memory_usage()

    # 磁盘
    disk_info = get_disk_usage()

    return SystemMetrics(
        cpu_percent=round(cpu_percent, 2),
        memory_percent=round(mem_info["percent"], 2),
        memory_used_mb=mem_info["used_mb"],
        memory_total_mb=mem_info["total_mb"],
        disk_percent=round(disk_info["percent"], 2),
        disk_used_gb=disk_info["used_gb"],
        disk_total_gb=disk_info["total_gb"],
        timestamp=datetime.now(timezone.utc),
    )


def get_system_info() -> dict[str, any]:
    """
    获取系统基本信息（静态信息，不需要频繁采集）

    Returns:
        dict: 包含CPU核心数、内存总量、磁盘总量等静态信息
    """
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_logical_cores": cpu_count,
        "cpu_physical_cores": cpu_count_physical,
        "memory_total_mb": round(mem.total / (1024 * 1024), 2),
        "memory_total_gb": round(mem.total / (1024 * 1024 * 1024), 2),
        "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
        "platform": "linux",  # 简化，实际可用platform模块
        "boot_time": datetime.fromtimestamp(
            psutil.boot_time(), tz=timezone.utc
        ).isoformat(),
    }


def get_process_info(pid: Optional[int] = None) -> dict[str, any]:
    """
    获取指定进程的资源占用情况
    用于监控后端服务自身的内存占用

    Args:
        pid: 进程ID，None表示当前进程

    Returns:
        dict: 进程资源使用情况
    """
    try:
        proc = psutil.Process(pid)
        mem_info = proc.memory_info()
        return {
            "pid": proc.pid,
            "name": proc.name(),
            "memory_mb": round(mem_info.rss / (1024 * 1024), 2),
            "memory_percent": round(proc.memory_percent(), 2),
            "cpu_percent": round(proc.cpu_percent(interval=0.1), 2),
            "threads": proc.num_threads(),
            "status": proc.status(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return {"error": "无法获取进程信息"}
