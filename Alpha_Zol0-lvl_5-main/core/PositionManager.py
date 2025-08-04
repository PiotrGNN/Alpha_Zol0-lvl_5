# PositionManager.py – Śledzenie pozycji

class PositionManager:
    def __init__(self):
        self.positions = {}  # symbol -> position dict
        self.closed = []

    def update_position(self, symbol, order):
        # order: {amount, side, price}
        pos = self.positions.get(symbol)
        if order["side"] in ["buy", "sell"]:
            # Open or update position
            entry_price = order.get("price")
            if not pos:
                self.positions[symbol] = {
                    "side": order["side"],
                    "amount": order["amount"],
                    "entry_price": entry_price,
                    "timestamp": order.get("timestamp")
                }
            else:
                # Update amount/side, keep entry_price if not closing
                self.positions[symbol].update({
                    "side": order["side"],
                    "amount": order["amount"]
                })
        elif order["side"] == "close":
            # Zamknięcie pozycji
            if pos:
                pos["close_timestamp"] = order.get("timestamp")
                self.closed.append(pos)
                del self.positions[symbol]

    def get_position(self, symbol):
        return self.positions.get(symbol)

    def get_status(self):
        return {s: p["side"] for s, p in self.positions.items()}
