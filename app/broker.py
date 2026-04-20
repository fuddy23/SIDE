from __future__ import annotations

from dataclasses import dataclass


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
    """Placeholder for moomoo OpenAPI integration.

    Implement with actual OpenAPI auth + order calls before live trading.
    """

    def __init__(self, host: str, port: int, unlock_password: str) -> None:
        self.host = host
        self.port = port
        self.unlock_password = unlock_password

    def place_order(self, order: Order) -> dict:
        raise NotImplementedError(
            "moomoo OpenAPI integration is not implemented in this scaffold yet."
        )
