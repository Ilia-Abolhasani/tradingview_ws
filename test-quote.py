from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td
from src.tradingview_ws.symbol import Symbol


def callbackFunc(s):
    print(s)


if __name__ == "__main__":
    symbols = [
        Symbol("XAUUSD", "cfd"),
        Symbol("DJI", "index"),
    ]
    username = "test"
    password = "test"
    trading = td.TradingViewWs(username, password)
    trading.realtime_quote(symbols, callbackFunc)
