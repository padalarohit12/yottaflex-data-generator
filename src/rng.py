"""
Central RNG for deterministic generation
"""
import random

_rng = None

def get_rng(seed=None):
    global _rng
    if _rng is None:
        if seed is None:
            from .config import config
            seed = config.seed
        _rng = random.Random(seed)
    return _rng

def reset_rng(seed=None):
    global _rng
    if seed is None:
        from .config import config
        seed = config.seed
    _rng = random.Random(seed)
    return _rng
