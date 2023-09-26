from __future__ import print_function

import re
import time
import json
import random
import string
import requests
import threading
from websocket import create_connection
from src.tradingview_ws.colorful_print import ColorfulPrint as cp

import pandas as pd
from datetime import datetime
from time import localtime

_API_URL_ = 'https://symbol-search.tradingview.com/symbol_search'
_WS_URL_ = "wss://data.tradingview.com/socket.io/websocket"


class TradingViewWs():
    def __init__(self, ticker, market, username=None, password=None):
        self.ticker = ticker.upper()
        self.market = market
        self._ws_url = _WS_URL_
        self._api_url = _API_URL_
        # self.token = self.get_auth_token(username, password)
        self.token = ""
        if (self.token == ''):
            self.token = "unauthorized_user_token"
        self.datas = []

    def get_auth_token(self, username, password):
        if not username or not password:
            return ''

        sign_in_url = 'https://www.tradingview.com/accounts/signin/'

        data = {"username": username, "password": password, "remember": "on"}
        headers = {
            'Referer': 'https://www.tradingview.com'
        }
        response = requests.post(url=sign_in_url, data=data, headers=headers)
        auth_token = response.json()['user']['auth_token']
        return auth_token

    def search(self, query, type):
        # type = 'stock' | 'futures' | 'forex' | 'cfd' | 'crypto' | 'index' | 'economic'
        # query = what you want to search!
        # it returns first matching item
        res = requests.get(
            f"{self._api_url}?text={query}&type={type}"
        )
        if res.status_code == 200:
            res = res.json()
            assert len(res) != 0, "Nothing Found."
            return res[0]
        else:
            print("Network Error!")
            exit(1)

    def generate_session(self, type):
        string_length = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters)
                                for i in range(string_length))
        return type + random_string

    def prepend_header(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    def construct_message(self, func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def create_message(self, func, paramList):
        return self.prepend_header(self.construct_message(func, paramList))

    def send_message(self, ws, func, args):
        mess = self.create_message(func, args)
        cp.print_green(mess)
        ws.send(mess)

    def send_ping_packet(self, ws, result):
        ping_str = re.findall(".......(.*)", result)
        if len(ping_str) != 0:
            ping_str = ping_str[0]
            ws.send("~m~" + str(len(ping_str)) + "~m~" + ping_str)

    def socket_quote(self, ws, callback):
        while True:
            try:
                result = ws.recv()
                cp.print_red(result)
                if "quote_completed" in result or "session_id" in result:
                    continue

                res = re.findall("^.*?({.*)$", result)
                if len(res) != 0:
                    jsonres = json.loads(res[0])

                    if jsonres["m"] == "qsd":
                        symbol = jsonres["p"][1]["n"]
                        price = jsonres["p"][1]["v"]["lp"]
                        callback({"symbol": symbol, "price": price})
                else:
                    # ping packet
                    self.send_ping_packet(ws, result)
            except KeyboardInterrupt:
                break
            except:
                continue

    def get_symbol_id(self, pair, market):
        data = self.search(pair, market)

        symbol_name = data["symbol"]
        if data['type'] == 'futures':
            symbol_name = data["contracts"][0]["symbol"]

        broker = data["exchange"]
        symbol_id = f"{broker.upper()}:{symbol_name.upper()}"
        return symbol_id

    def realtime_quote(self, callback):
        # serach btcusdt from crypto category
        symbol_id = self.get_symbol_id(self.ticker, self.market)

        # create tunnel
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        ws = create_connection(self._ws_url, headers=headers)
        session = self.generate_session("qs_")

        # Send messages
        self.send_message(ws, "set_data_quality", ["low"])
        if self.token:
            self.send_message(ws, "set_auth_token", [self.token])
        else:
            self.send_message(ws, "set_auth_token", [
                              "unauthorized_user_token"])
        self.send_message(ws, "set_locale", ["en", "US"])

        self.send_message(ws, "quote_create_session", [session])

        self.send_message(ws, "quote_set_fields", [session, "lp"])
        self.send_message(ws, "quote_add_symbols", [session, symbol_id])

        # Start job
        self.socket_quote(ws, callback)

    def realtime_bar_chart(self, interval, total_candle, callback):
        # serach btcusdt from crypto category
        symbol_id = self.get_symbol_id(self.ticker, self.market)

        # create sessions
        session = self.generate_session("qs_")
        chart_session = self.generate_session("cs_")

        # connect to websocket
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        ws = create_connection(self._ws_url, headers=headers)

        def receive_thread():
            while True:
                try:
                    result = ws.recv()
                    if re.search(r'~m~(\d+)~m~~h~(\d+)', result):
                        ws.send(result)
                        continue
                    result = re.split(r'~m~', result)
                    result = [res for res in result if len(res) > 0]
                    result = result[1::2]
                    cp.print_blue("\n\n".join(result))
                    if not result:
                        continue

                    for item in result:
                        data = json.loads(item)
                        if ("session_id" in data):
                            continue

                        if ('m' not in data):
                            print(data)
                            pass
                        method = data['m']
                        if method == "qsd":
                            session, temp = data["p"]
                            n = temp["n"]
                            s = temp["s"]
                            v = temp["v"]
                            pass
                        elif method == "du":
                            pass
                        elif method == "quote_completed":
                            session, temp = data["p"]
                            pass
                        elif method == "timescale_update":
                            temp = data["p"]
                            pass
                        elif method == "symbol_resolved":
                            session, sym_id, temp = data["p"]
                            pass
                        elif method == "series_loading":
                            pass
                        elif method == "series_completed":
                            pass
                        else:
                            pass
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print("=========except", datetime.now(), e)
                    if ('closed' in str(e) or 'lost' in str(e)):
                        print("=========try")
                        self.realtime_bar_chart(5, 1, callback)

        # Start the receive thread
        receive_thread = threading.Thread(target=receive_thread)
        # Set as a daemon thread to exit when the main program exits
        receive_thread.daemon = True
        receive_thread.start()

        # Then send a message through the tunnel
        messages = []
        messages.append(["set_auth_token", [self.token]])
        messages.append(["set_locale", ["en", "US"]])
        messages.append(["chart_create_session", [chart_session, ""]])
        messages.append(["switch_timezone", [
            chart_session, "America/Vancouver"
        ]])
        messages.append(["switch_timezone", [
            chart_session, "America/Vancouver"
        ]])
        messages.append(["quote_create_session", [session]])
        data = "={\"adjustment\":\"splits\",\"session\":\"extended\",\"settlement-as-close\":false,\"symbol\":\"" + symbol_id + "\"}"
        messages.append(["quote_add_symbols", [session, data]])
        messages.append(["resolve_symbol", [
            chart_session, "sds_sym_1", data
        ]])
        messages.append(["create_series", [
            chart_session, "sds_1", "s1", "sds_sym_1", "1S", 300, ""
        ]])
        messages.append(["quote_set_fields", [
            session,
            "ch",
            "chp",
            "current_session",
            "description",
            "local_description",
            "language",
            "exc hange",
            "fractional",
            "is_tradable",
            "lp",
            "lp_time",
            "minmov",
            "minmove2",
            "original_name",
            "pricescale",
            "pro_name",
            "short_name",
            "type",
            "update_mode",
            "volume",
            "currency_code",
            "rchp",
            "rtc"
        ]])
        messages.append(["quote_add_symbols", [session, symbol_id]])
        messages.append(["quote_fast_symbols", [session, data]])
        messages.append(["quote_fast_symbols", [session, symbol_id]])
        temp = "={\"symbol\":\"" + symbol_id + \
            "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"
        messages.append(["resolve_symbol", [
            chart_session, "symbol_1", temp
        ]])
        messages.append(["request_more_tickmarks", [
            chart_session,
            "sds_1",
            10
        ]])
        messages.append(["request_more_data", [
            chart_session,
            "sds_1",
            734
        ]])
        while True:
            try:
                for mess in messages:
                    self.send_message(ws, mess[0], mess[1])
                    time.sleep(0.2)
                messages = []
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
