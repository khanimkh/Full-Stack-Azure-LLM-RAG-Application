from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "infra" / "scripts" / "export_env_config.py"
SPEC = spec_from_file_location("env_export", SCRIPT_PATH)
MODULE = module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_key_map_contains_traffic_mode() -> None:
    assert MODULE.KEY_MAP["trafficMode"] == "TRAFFIC_MODE"
