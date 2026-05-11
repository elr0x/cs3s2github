#!/usr/bin/env python3
"""
monitor.py - System & Container Metrics Monitoring Client
Knowledge Hub | CS3-IN-NCB | Task 4 / Task 9

Collects system metrics (CPU, memory, disk) using psutil and
Docker container metrics using the Docker SDK, then sends them
to the Monitoring API using the requests library.
Credentials are loaded securely from a .env file (python-dotenv).

Usage:
    python monitor.py                  # Single collection + send
    python monitor.py --interval 60    # Continuous mode, every 60 seconds
    python monitor.py --dry-run        # Collect and print, don't send
    python monitor.py --no-docker      # Skip Docker container metrics

Requirements:
    pip install psutil requests python-dotenv docker
"""

import os
import sys
import time
import socket
import logging
import argparse
from datetime import datetime

import psutil
import requests
from dotenv import load_dotenv

# Docker SDK is optional - gracefully skip if not available or no Docker socket
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

# -- Load environment variables from .env -----------------------
load_dotenv()

API_URL = os.getenv("MONITOR_API_URL")      # e.g. https://app-monitoring-knowledgehub.azurewebsites.net/api/v1
API_KEY = os.getenv("MONITOR_API_KEY")       # same key configured on the server

# -- Logging ----------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("monitor")


# -- System Metric Collection -----------------------------------
def collect_metrics() -> list[dict]:
    """Collect system metrics using psutil and return as list of dicts."""
    hostname = socket.gethostname()
    metrics = []

    # CPU usage (%)
    cpu_percent = psutil.cpu_percent(interval=1)
    metrics.append({
        "source_host": hostname,
        "source_type": "onprem",
        "metric_name": "cpu_percent",
        "metric_value": cpu_percent,
        "unit": "%",
        "status": _threshold_status(cpu_percent, warn=75, crit=90)
    })

    # Memory usage (%)
    mem = psutil.virtual_memory()
    metrics.append({
        "source_host": hostname,
        "source_type": "onprem",
        "metric_name": "memory_percent",
        "metric_value": mem.percent,
        "unit": "%",
        "status": _threshold_status(mem.percent, warn=80, crit=95)
    })

    # Memory available (GB)
    mem_available_gb = round(mem.available / (1024 ** 3), 2)
    metrics.append({
        "source_host": hostname,
        "source_type": "onprem",
        "metric_name": "memory_available_gb",
        "metric_value": mem_available_gb,
        "unit": "GB",
        "status": "OK"
    })

    # Disk usage per partition
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue

        disk_percent = usage.percent
        disk_free_gb = round(usage.free / (1024 ** 3), 2)

        metrics.append({
            "source_host": hostname,
            "source_type": "onprem",
            "metric_name": f"disk_percent_{partition.mountpoint}",
            "metric_value": disk_percent,
            "unit": "%",
            "status": _threshold_status(disk_percent, warn=80, crit=95)
        })
        metrics.append({
            "source_host": hostname,
            "source_type": "onprem",
            "metric_name": f"disk_free_gb_{partition.mountpoint}",
            "metric_value": disk_free_gb,
            "unit": "GB",
            "status": "OK"
        })

    return metrics


# -- Docker Container Metric Collection -------------------------
def collect_docker_metrics() -> list[dict]:
    """
    Collect metrics for all running Docker containers using the Docker SDK.
    Returns a list of metric dicts compatible with the Monitoring API.
    Falls back gracefully if Docker is not available or socket is not accessible.
    """
    if not DOCKER_AVAILABLE:
        logger.warning("Docker SDK not installed. Skipping container metrics. Run: pip install docker")
        return []

    try:
        client = docker.from_env()
        containers = client.containers.list()
    except Exception as e:
        logger.warning(f"Cannot connect to Docker socket: {e}. Skipping container metrics.")
        return []

    metrics = []
    hostname = socket.gethostname()

    for container in containers:
        name = container.name
        source_host = f"{hostname}/{name}"

        try:
            # Get raw stats (non-streaming, one snapshot)
            stats = container.stats(stream=False)

            # -- CPU % calculation ----------------------------------
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                        stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                           stats["precpu_stats"]["system_cpu_usage"]
            num_cpus = stats["cpu_stats"].get("online_cpus") or \
                       len(stats["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))

            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = round((cpu_delta / system_delta) * num_cpus * 100.0, 2)

            metrics.append({
                "source_host": source_host,
                "source_type": "docker",
                "metric_name": "container_cpu_percent",
                "metric_value": cpu_percent,
                "unit": "%",
                "status": _threshold_status(cpu_percent, warn=75, crit=90)
            })

            # -- Memory usage ---------------------------------------
            mem_usage = stats["memory_stats"].get("usage", 0)
            mem_limit = stats["memory_stats"].get("limit", 1)
            # Subtract cache from usage (more accurate real usage)
            cache = stats["memory_stats"].get("stats", {}).get("cache", 0)
            mem_real = max(mem_usage - cache, 0)
            mem_percent = round((mem_real / mem_limit) * 100, 2) if mem_limit > 0 else 0.0
            mem_mb = round(mem_real / (1024 ** 2), 2)

            metrics.append({
                "source_host": source_host,
                "source_type": "docker",
                "metric_name": "container_memory_percent",
                "metric_value": mem_percent,
                "unit": "%",
                "status": _threshold_status(mem_percent, warn=80, crit=95)
            })
            metrics.append({
                "source_host": source_host,
                "source_type": "docker",
                "metric_name": "container_memory_mb",
                "metric_value": mem_mb,
                "unit": "MB",
                "status": "OK"
            })

            # -- Network I/O ----------------------------------------
            net_stats = stats.get("networks", {})
            total_rx = sum(v.get("rx_bytes", 0) for v in net_stats.values())
            total_tx = sum(v.get("tx_bytes", 0) for v in net_stats.values())

            metrics.append({
                "source_host": source_host,
                "source_type": "docker",
                "metric_name": "container_net_rx_mb",
                "metric_value": round(total_rx / (1024 ** 2), 2),
                "unit": "MB",
                "status": "OK"
            })
            metrics.append({
                "source_host": source_host,
                "source_type": "docker",
                "metric_name": "container_net_tx_mb",
                "metric_value": round(total_tx / (1024 ** 2), 2),
                "unit": "MB",
                "status": "OK"
            })

            logger.debug(f"Container '{name}': CPU={cpu_percent}%, MEM={mem_mb}MB")

        except Exception as e:
            logger.warning(f"Failed to collect stats for container '{name}': {e}")
            continue

    logger.info(f"Collected Docker metrics for {len(containers)} containers.")
    return metrics


def _threshold_status(value: float, warn: float, crit: float) -> str:
    """Determine metric status based on thresholds."""
    if value >= crit:
        return "CRITICAL"
    elif value >= warn:
        return "WARNING"
    return "OK"


# -- Send Metrics to API ----------------------------------------
def send_metric(metric: dict) -> bool:
    """Send a single metric to the Monitoring API using requests."""
    endpoint = f"{API_URL}/metrics"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(endpoint, json=metric, headers=headers, timeout=10)

        if response.status_code == 201:
            logger.info(f"SENT | {metric['metric_name']}={metric['metric_value']} -> {response.status_code}")
            return True
        else:
            logger.warning(f"FAIL | {metric['metric_name']} -> {response.status_code}: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        logger.error(f"CONN ERROR | Cannot reach {endpoint}")
        return False
    except requests.exceptions.Timeout:
        logger.error(f"TIMEOUT | {endpoint} did not respond within 10s")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"REQUEST ERROR | {e}")
        return False


def send_all_metrics(metrics: list[dict]) -> dict:
    """Send all collected metrics and return a summary."""
    sent = 0
    failed = 0
    for metric in metrics:
        if send_metric(metric):
            sent += 1
        else:
            failed += 1
    return {"sent": sent, "failed": failed, "total": len(metrics)}


# -- CLI --------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="System & Container Metrics Monitoring Client"
    )
    parser.add_argument(
        "--interval", type=int, default=0,
        help="Seconds between collection cycles (0 = single run, default: 0)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Collect and print metrics without sending to API"
    )
    parser.add_argument(
        "--no-docker", action="store_true",
        help="Skip Docker container metrics collection"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate configuration
    if not args.dry_run:
        if not API_URL:
            logger.error("MONITOR_API_URL not set. Add it to .env or set environment variable.")
            sys.exit(1)
        if not API_KEY:
            logger.error("MONITOR_API_KEY not set. Add it to .env or set environment variable.")
            sys.exit(1)
        logger.info(f"Target API: {API_URL}")

    logger.info(f"Hostname: {socket.gethostname()}")
    logger.info(f"Mode: {'Continuous (every %ds)' % args.interval if args.interval > 0 else 'Single run'}")
    logger.info(f"Docker metrics: {'disabled' if args.no_docker else 'enabled'}")
    logger.info("-" * 50)

    while True:
        # Collect system metrics
        metrics = collect_metrics()

        # Collect Docker container metrics (unless disabled)
        if not args.no_docker:
            docker_metrics = collect_docker_metrics()
            metrics.extend(docker_metrics)

        if args.dry_run:
            logger.info(f"Collected {len(metrics)} metrics (dry-run, not sending):")
            for m in metrics:
                logger.info(f"  {m['metric_name']:40s} = {m['metric_value']:>10} {m['unit']:>4}  [{m['status']}]")
        else:
            result = send_all_metrics(metrics)
            logger.info(f"Summary: {result['sent']} sent, {result['failed']} failed, {result['total']} total")

        if args.interval <= 0:
            break

        logger.info(f"Sleeping {args.interval}s until next collection...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
