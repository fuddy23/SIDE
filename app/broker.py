from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Order:
    symbol: str
    side: str  # BUY / SELL
    qty: int
    price: float


class PaperBroker:
    """Paper broker for local development/testing."""

    def place_order(self, order: Order) -> dict:
        return {
            "status": "FILLED",
            "symbol": order.symbol,
            "side": order.side,
            "qty": order.qty,
            "price": order.price,
        }


class MoomooBroker:
    """moomoo OpenAPI broker adapter.

    Requires `futu` package and moomoo OpenD running locally.
    """

    def __init__(
        self,
        host: str,
        port: int,
        unlock_password: str,
        trd_env: str = "SIMULATE",
        market: str = "US",
    ) -> None:
        self.host = host
        self.port = port
        self.unlock_password = unlock_password
        self.trd_env = trd_env.upper()
        self.market = market.upper()

        try:
            import futu as ft
        except ImportError as exc:
            raise RuntimeError(
                "futu package is required. Install with: pip install futu-api"
            ) from exc

        self._ft = ft
        self._trd_ctx = self._build_trade_ctx()
        self._unlock_trade()

    def _build_trade_ctx(self) -> Any:
        if self.market == "US":
            return self._ft.OpenSecTradeContext(
                filter_trdmarket=self._ft.TrdMarket.US,
                host=self.host,
                port=self.port,
                security_firm=self._ft.SecurityFirm.FUTUSECURITIES,
            )
        if self.market == "HK":
            return self._ft.OpenSecTradeContext(
                filter_trdmarket=self._ft.TrdMarket.HK,
                host=self.host,
                port=self.port,
                security_firm=self._ft.SecurityFirm.FUTUSECURITIES,
            )
        raise ValueError("market must be US or HK")

    def _unlock_trade(self) -> None:
        ret, data = self._trd_ctx.unlock_trade(password=self.unlock_password)
        if ret != self._ft.RET_OK:
            raise RuntimeError(f"unlock_trade failed: {data}")

    def place_order(self, order: Order) -> dict:
        trd_side = self._ft.TrdSide.BUY if order.side == "BUY" else self._ft.TrdSide.SELL
        trd_env = (
            self._ft.TrdEnv.SIMULATE
            if self.trd_env == "SIMULATE"
            else self._ft.TrdEnv.REAL
        )
        price = round(float(order.price), 3)
        ret, data = self._trd_ctx.place_order(
            price=price,
            qty=order.qty,
            code=order.symbol,
            trd_side=trd_side,
            order_type=self._ft.OrderType.NORMAL,
            trd_env=trd_env,
        )
        if ret != self._ft.RET_OK:
            raise RuntimeError(f"place_order failed: {data}")
        row = data.iloc[0].to_dict()
        return {
            "status": "SUBMITTED",
            "order_id": row.get("order_id"),
            "symbol": row.get("code", order.symbol),
            "side": order.side,
            "qty": order.qty,
            "price": price,
        }

    def close(self) -> None:
        if hasattr(self, "_trd_ctx"):
            self._trd_ctx.close()
