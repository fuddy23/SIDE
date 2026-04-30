from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    db_path: Path = Path("data/trades.db")
    initial_cash: float = 1_000_000.0
    risk_per_trade: float = 0.005
    buy_threshold: float = 0.58
    sell_threshold: float = 0.42
    require_manual_approval: bool = False
    broker_mode: str = "paper"  # "paper" | "moomoo"
    moomoo_host: str = "127.0.0.1"
    moomoo_port: int = 11111
    moomoo_unlock_password: str = ""
    moomoo_trd_env: str = "SIMULATE"  # "SIMULATE" | "REAL"
    moomoo_market: str = "US"  # "US" | "HK"


CONFIG = AppConfig()
