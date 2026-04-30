from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable

import pandas as pd

from app.broker import MoomooBroker, Order, PaperBroker
from app.config import AppConfig
from app.db import get_conn, init_db
from app.model import PriceDirectionModel


@dataclass
class Portfolio:
    cash: float
    qty: int = 0


class AutoTrader:
    def __init__(
        self,
        config: AppConfig,
        approver: Callable[[str, str, int, float, float, str], tuple[bool, str]] | None = None,
    ) -> None:
        self.config = config
        self.model = PriceDirectionModel()
        self.broker = self._build_broker()
        self.portfolio = Portfolio(cash=config.initial_cash)
        self.approver = approver or self._console_approver

        self.conn = get_conn(config.db_path)
        init_db(self.conn)

    def on_new_data(self, symbol: str, df: pd.DataFrame) -> dict | None:
        prob = self.model.predict_proba_latest(df)
        px = float(df["close"].iloc[-1])

        if prob >= self.config.buy_threshold and self.portfolio.cash > 0:
            qty = self._calc_qty(px)
            if qty > 0:
                reason = (
                    f"買いシグナル: 上昇確率 {prob:.2%} が買い閾値 {self.config.buy_threshold:.2%} を上回ったため"
                )
                return self._handle_signal(symbol, "BUY", qty, px, prob, reason)

        if prob <= self.config.sell_threshold and self.portfolio.qty > 0:
            qty = self.portfolio.qty
            reason = (
                f"売りシグナル: 上昇確率 {prob:.2%} が売り閾値 {self.config.sell_threshold:.2%} を下回ったため"
            )
            return self._handle_signal(symbol, "SELL", qty, px, prob, reason)

        self._write_equity(px)
        return None

    def _calc_qty(self, px: float) -> int:
        budget = self.portfolio.cash * self.config.risk_per_trade
        return max(int(budget // px), 0)

    def _build_broker(self) -> PaperBroker | MoomooBroker:
        if self.config.broker_mode.lower() == "moomoo":
            return MoomooBroker(
                host=self.config.moomoo_host,
                port=self.config.moomoo_port,
                unlock_password=self.config.moomoo_unlock_password,
                trd_env=self.config.moomoo_trd_env,
                market=self.config.moomoo_market,
            )
        return PaperBroker()

    def _handle_signal(
        self, symbol: str, side: str, qty: int, price: float, prob: float, reason: str
    ) -> dict | None:
        approved = True
        note = "auto-approved"
        if self.config.require_manual_approval:
            approved, note = self.approver(symbol, side, qty, price, prob, reason)
        self._write_signal(symbol, side, qty, price, prob, reason, approved, note)
        if not approved:
            return None
        return self._execute(symbol, side, qty, price, prob, reason)

    def _execute(
        self,
        symbol: str,
        side: str,
        qty: int,
        price: float,
        prob: float,
        reason: str,
    ) -> dict:
        result = self.broker.place_order(Order(symbol=symbol, side=side, qty=qty, price=price))

        if side == "BUY":
            self.portfolio.cash -= qty * price
            self.portfolio.qty += qty
            pnl = 0.0
        else:
            self.portfolio.cash += qty * price
            self.portfolio.qty -= qty
            pnl = qty * price

        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO trades (ts, symbol, side, qty, price, predicted_prob, reason, pnl)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (now, symbol, side, qty, price, prob, reason, pnl),
        )
        self.conn.commit()
        self._write_equity(price)
        return result

    def _write_signal(
        self,
        symbol: str,
        side: str,
        qty: int,
        price: float,
        prob: float,
        reason: str,
        approved: bool,
        note: str,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute(
            """
            INSERT INTO signals (ts, symbol, side, qty, price, predicted_prob, reason, approved, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (now, symbol, side, qty, price, prob, reason, int(approved), note),
        )
        self.conn.commit()

    def _write_equity(self, price: float) -> None:
        now = datetime.now(timezone.utc).isoformat()
        position_value = self.portfolio.qty * price
        total = self.portfolio.cash + position_value
        self.conn.execute(
            """
            INSERT INTO equity_curve (ts, cash, position_value, total_equity)
            VALUES (?, ?, ?, ?)
            """,
            (now, self.portfolio.cash, position_value, total),
        )
        self.conn.commit()

    @staticmethod
    def _console_approver(
        symbol: str, side: str, qty: int, price: float, prob: float, reason: str
    ) -> tuple[bool, str]:
        print("\n=== 取引承認リクエスト ===")
        print(f"銘柄: {symbol}")
        print(f"売買: {side}")
        print(f"数量: {qty}")
        print(f"価格: {price:.2f}")
        print(f"上昇確率: {prob:.2%}")
        print(f"理由: {reason}")
        ans = input("実行しますか？ [y/N]: ").strip().lower()
        if ans in {"y", "yes"}:
            return True, "manual-approved"
        return False, "manual-rejected"
