from dataclasses import replace

from app.config import CONFIG
from app.sample_data import generate_ohlcv
from app.trader import AutoTrader


if __name__ == "__main__":
    symbol = "AAPL"
    df = generate_ohlcv(600)
    cfg = replace(CONFIG, require_manual_approval=True)
    trader = AutoTrader(cfg)

    for i in range(80, len(df)):
        trader.on_new_data(symbol, df.iloc[:i].copy())

    print("Done. Trades saved to", cfg.db_path)
