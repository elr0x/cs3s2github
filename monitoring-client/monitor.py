#!/usr/bin/env python3
"""
monitor.py — System Metrics Monitoring Client
Knowledge Hub | CS2-IN-NCB | Task 4

Collects system metrics (CPU, memory, disk) using psutil
and sends them to the Monitoring API using the requests library.
Credentials are loaded securely from a .env file (python-dotenv).

Usage:
    python monitor.py                  # Single collection + send
    python monitor.py --interval 60    # Continuous mode, every 60 seconds
    python monitor.py --dry-run        # Collect and print, don't send

Requirements:
    pip install psutil requests python-dotenv
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

# ── Load environment variables from .env ──────────────────────
load_dotenv()

API_URL = os.getenv("MONITOR_API_URL")      # e.g. https://app-knowledgehub-api.azurewebsites.net
API_KEY = os.getenv("MONITOR_API_KEY")       # same key configured on the server

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("monitor")


# ── Metric Collection ─────────────────────────────────────────
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


def _threshold_status(value: float, warn: float, crit: float) -> str:
    """Determine metric status based on thresholds."""
    if value >= crit:
        return "CRITICAL"
    elif value >= warn:
        return "WARNING"
    return "OK"


# ── Send Metrics to API ──────────────────────────────────────
def send_metric(metric: dict) -> bool:
    """Send a single metric to the Monitoring API using requests."""
    endpoint = f"{API_URL}/api/v1/metrics"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }

    try:
        response = requests.post(endpoint, json=metric, headers=headers, timeout=10)

        if response.status_code == 201:
            logger.info(f"SENT | {metric['metric_name']}={metric['metric_value']} → {response.status_code}")
            return True
        else:
            logger.warning(f"FAIL | {metric['metric_name']} → {response.status_code}: {response.text}")
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


# ── CLI ───────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="System Metrics Monitoring Client — Collects and sends metrics to the API"
    )
    parser.add_argument(
        "--interval", type=int, default=0,
        help="Seconds between collection cycles (0 = single run, default: 0)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Collect and print metrics without sending to API"
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
    logger.info(f"Mode: {'Continuous (every {0}s)'.format(args.interval) if args.interval > 0 else 'Single run'}")
    logger.info("-" * 50)

    while True:
        metrics = collect_metrics()

        if args.dry_run:
            logger.info(f"Collected {len(metrics)} metrics (dry-run, not sending):")
            for m in metrics:
                logger.info(f"  {m['metric_name']:30s} = {m['metric_value']:>10} {m['unit']:>4}  [{m['status']}]")
        else:
            result = send_all_metrics(metrics)
            logger.info(f"Summary: {result['sent']} sent, {result['failed']} failed, {result['total']} total")

        if args.interval <= 0:
            break

        logger.info(f"Sleeping {args.interval}s until next collection...")
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
