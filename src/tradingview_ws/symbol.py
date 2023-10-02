from __future__ import print_function

import re
import time
import json
import random
import string
import requests
import threading
from websocket import create_connection
from .colorful_print import ColorfulPrint as cp

import pandas as pd
from datetime import datetime
from time import localtime

_API_URL_ = 'https://symbol-search.tradingview.com/symbol_search'
MARKET_TYPES = ['stock', 'futures', 'forex',
                'cfd', 'crypto', 'index', 'economic']


class Symbol():
    def __init__(self, pair, market):
        if market not in MARKET_TYPES:
            print("Invalid market!")
            exit(1)
        self.pair = pair.upper()
        self.market = market
        self.id = self.get_symbol_id()
        self.session = None
        self.date = []

    def search(self, query, type):
        # type = 'stock' | 'futures' | 'forex' | 'cfd' | 'crypto' | 'index' | 'economic'
        # query = what you want to search!
        # it returns first matching item
        res = requests.get(
            f"{_API_URL_}?text={query}&type={type}"
        )
        if res.status_code == 200:
            res = res.json()
            assert len(res) != 0, "Nothing Found."
            return res[0]
        else:
            print("Network Error!")
            exit(1)

    def get_symbol_id(self):
        data = self.search(self.pair, self.market)

        symbol_name = data["symbol"]
        if data['type'] == 'futures':
            symbol_name = data["contracts"][0]["symbol"]

        broker = data["exchange"]
        symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
        return symbol_id
