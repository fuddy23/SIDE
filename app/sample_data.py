from __future__ import annotations

import numpy as np
import pandas as pd


def generate_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=0.0003, scale=0.01, size=n)
    price = 100 * np.exp(np.cumsum(returns))
    volume = rng.integers(100_000, 2_000_000, size=n)
    ts = pd.date_range(end=pd.Timestamp.utcnow(), periods=n, freq="min")
    return pd.DataFrame({"ts": ts, "close": price, "volume": volume})
