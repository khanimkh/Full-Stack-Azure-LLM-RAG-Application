from __future__ import annotations

import json
import sys
from pathlib import Path


KEY_MAP = {
    "minReplicas": "MIN_REPLICAS",
    "maxReplicas": "MAX_REPLICAS",
    "httpConcurrency": "HTTP_CONCURRENCY",
    "canaryWeight": "CANARY_WEIGHT",
    "trafficMode": "TRAFFIC_MODE",
    "cpuAlertThreshold": "CPU_ALERT_THRESHOLD",
}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: export_env_config.py <config.json>")

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for key, env_name in KEY_MAP.items():
        if key in payload:
            print(f"{env_name}={payload[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
