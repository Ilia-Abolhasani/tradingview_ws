from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import src.tradingview_ws as td
from src.tradingview_ws.symbol import Symbol


def callbackFunc(datas):
    print(len(datas), datas[len(datas)-1])


if __name__ == "__main__":
    symbols = [
        Symbol("XAUUSD", "cfd"),
        Symbol("DJI", "index"),
    ]
    username = "test"
    password = "test"
    trading = td.TradingViewWs(username, password)
    interval = 5
    total_candle = 240
    trading.realtime_bar_chart(symbols, interval, total_candle, callbackFunc)
