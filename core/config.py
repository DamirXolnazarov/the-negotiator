import yaml
from pathlib import Path

_cache = {}


def load_config(vertical: str = "moving") -> dict:
    """Load a vertical's config, e.g. load_config('moving') -> config/moving.yaml"""
    if vertical in _cache:
        return _cache[vertical]

    path = Path(f"config/{vertical}.yaml")
    if not path.exists():
        raise FileNotFoundError(f"No config found for vertical '{vertical}' at {path}")

    with open(path) as f:
        cfg = yaml.safe_load(f)

    _cache[vertical] = cfg
    return cfg