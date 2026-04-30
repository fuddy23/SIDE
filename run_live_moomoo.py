import os
from dataclasses import replace

from app.config import CONFIG
from app.sample_data import generate_ohlcv
from app.trader import AutoTrader


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


if __name__ == "__main__":
    cfg = replace(
        CONFIG,
        broker_mode="moomoo",
        require_manual_approval=True,
        moomoo_host=env("MOOMOO_HOST", "127.0.0.1"),
        moomoo_port=int(env("MOOMOO_PORT", "11111")),
        moomoo_unlock_password=env("MOOMOO_UNLOCK_PASSWORD"),
        moomoo_trd_env=env("MOOMOO_TRD_ENV", "SIMULATE"),
        moomoo_market=env("MOOMOO_MARKET", "US"),
    )

    symbol = env("TRADE_SYMBOL", "US.AAPL")
    df = generate_ohlcv(400)
    trader = AutoTrader(cfg)

    for i in range(80, len(df)):
        trader.on_new_data(symbol, df.iloc[:i].copy())

    print("Done. Trades saved to", cfg.db_path)
