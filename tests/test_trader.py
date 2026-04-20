from app.config import AppConfig
from app.sample_data import generate_ohlcv
from app.trader import AutoTrader


def test_trader_writes_equity(tmp_path) -> None:
    db_path = tmp_path / "trades.db"
    cfg = AppConfig(db_path=db_path)
    trader = AutoTrader(cfg)

    df = generate_ohlcv(180)
    for i in range(80, 120):
        trader.on_new_data("AAPL", df.iloc[:i].copy())

    cur = trader.conn.execute("SELECT COUNT(*) FROM equity_curve")
    cnt = cur.fetchone()[0]
    assert cnt > 0


def test_trader_requires_manual_approval_when_enabled(tmp_path) -> None:
    db_path = tmp_path / "trades.db"
    cfg = AppConfig(
        db_path=db_path,
        buy_threshold=0.0,
        sell_threshold=0.0,
        require_manual_approval=True,
    )

    def reject_all(*_args):
        return False, "test-rejected"

    trader = AutoTrader(cfg, approver=reject_all)
    df = generate_ohlcv(120)
    trader.on_new_data("AAPL", df.iloc[:100].copy())

    trade_cnt = trader.conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
    signal_cnt = trader.conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
    approved = trader.conn.execute("SELECT approved FROM signals LIMIT 1").fetchone()[0]

    assert trade_cnt == 0
    assert signal_cnt >= 1
    assert approved == 0
