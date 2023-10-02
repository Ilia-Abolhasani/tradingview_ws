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
from src.tradingview_ws.dot_dict import DotDict

import pandas as pd
from datetime import datetime
from time import localtime

_API_URL_ = 'https://symbol-search.tradingview.com/symbol_search'
_WS_URL_ = "wss://data.tradingview.com/socket.io/websocket"


class TradingViewWs():
    def __init__(self, username=None, password=None, token=None):
        self._ws_url = _WS_URL_
        self._api_url = _API_URL_
        if token:
            self.token = token
        else:
            self.token = self.get_auth_token(username, password)
        if (self.token == ''):
            self.token = "unauthorized_user_token"
        self.ws = None

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

    def create_connection(self):
        headers = json.dumps({"Origin": "https://data.tradingview.com"})
        self.ws = create_connection(self._ws_url, headers=headers)
        self.send_message("set_auth_token", [self.token])
        self.send_message("set_locale", ["en", "US"])

    def generate_session(self, type):
        string_length = 12
        letters = string.ascii_lowercase
        random_string = "".join(random.choice(letters)
                                for i in range(string_length))
        return type + random_string

    def prepend_header(self, st):
        return "~m~" + str(len(st)) + "~m~" + st

    # message
    def construct_message(self, func, param_list):
        return json.dumps({"m": func, "p": param_list}, separators=(",", ":"))

    def create_message(self, func, paramList):
        return self.prepend_header(self.construct_message(func, paramList))

    def send_message(self, func, args):
        mess = self.create_message(func, args)
        # cp.print_green(mess)
        self.ws.send(mess)

    def send_ping_packet(self, result):
        ping_str = re.findall(".......(.*)", result)
        if len(ping_str) != 0:
            ping_str = ping_str[0]
            self.ws.send("~m~" + str(len(ping_str)) + "~m~" + ping_str)

    # Quote
    def realtime_quote(self, symbols, callback):
        start = True
        while True:
            try:
                if start:
                    self.create_connection()
                    session = self.generate_session("qs_")
                    self.send_message("set_data_quality", ["low"])
                    self.send_message("quote_create_session", [session])
                    self.send_message("set_data_quality", ["low"])
                    self.send_message("quote_set_fields", [
                                      session, "lp", "lp_time", "pricescale"])
                    symbols_id = [sym.id for sym in symbols]
                    self.send_message("quote_add_symbols", [
                                      session, *symbols_id])
                    start = False
                result = self.ws.recv()
                if re.search(r'~m~(\d+)~m~~h~(\d+)', result):
                    self.ws.send(result)
                    continue
                result = re.split(r'~m~', result)
                result = [res for res in result if len(res) > 0]
                result = result[1:: 2]
                # cp.print_blue("\n\n".join(result))
                if not result:
                    continue
                for item in result:
                    json_res = json.loads(item)
                    if ("session_id" in json_res):
                        continue
                    if ('m' not in json_res):
                        print(json_res)
                        pass
                    method = json_res['m']
                    if method == "qsd":
                        symbol = json_res["p"][1]["n"]
                        info = json_res["p"][1]["v"]
                        lp = info["lp"]
                        lp_time = info["lp_time"]
                        callback(DotDict({
                            "symbol": symbol,
                            "time": lp_time,
                            "price": lp,
                        }))
            except KeyboardInterrupt:
                break
            except Exception as e:
                if ('closed' in str(e) or 'lost' in str(e)):
                    print("========= try to connect again =========")
                    start = True
                else:
                    print("=========except", datetime.now(), e)

    # Chart
    # def socket_bar_chart(self, interval, callback):
    #     global chart_df
    #     chart_df = None
    #     while True:
    #         result = self.ws.recv()
    #         if re.search(r'~m~(\d+)~m~~h~(\d+)', result):
    #             self.ws.send(result)
    #             continue
    #         result = re.split(r'~m~', result)
    #         result = [res for res in result if len(res) > 0]
    #         result = result[1::2]
    #         # cp.print_blue("\n\n".join(result))
    #         if not result:
    #             continue

    #         for item in result:
    #             data = json.loads(item)
    #             if ("session_id" in data):
    #                 continue

    #             if ('m' not in data):
    #                 print(data)
    #                 pass
    #             method = data['m']
    #             if method == "qsd":
    #                 pass
    #             elif method == "du":
    #                 temp = data["p"]
    #                 temp = temp[1]
    #                 candle = temp['sds_1']['s'][0]['v']
    #                 cp.print_blue(str(candle))
    #                 pass
    #             elif method == "quote_completed":
    #                 pass
    #             elif method == "timescale_update":
    #                 p = data['p']
    #                 if "sds_1" in p[1]:
    #                     _data = [item['v']
    #                              for item in p[1]['sds_1']['s']]
    #                     chart_df = pd.DataFrame(data=_data,
    #                                             columns=["date", "open", "high", "low", "close", "volume"])
    #                     chart_df['date'] = chart_df['date'].apply(
    #                         lambda utc_timestamp:
    #                             datetime.utcfromtimestamp(
    #                                 utc_timestamp)
    #                     )
    #                 else:
    #                     pass
    #             elif method == "symbol_resolved":
    #                 session, sym_id, temp = data["p"]
    #             elif method == "symbol_resolved":
    #                 session, sym_id, temp = data["p"]
    #             elif method == "series_loading":
    #                 pass
    #             elif method == "series_completed":
    #                 pass
    #             else:
    #                 pass

    # def realtime_bar_chart(
    #         self,
    #         symbols,
    #         interval,
    #         total_candle,
    #         callback
    # ):
    #     # create sessions
    #     session = self.generate_session("qs_")
    #     temp_session = []
    #     for symbol in symbols:
    #         while True:
    #             session = self.generate_session("cs_")
    #             if session in temp_session:
    #                 continue
    #             temp_session.append(session)
    #             break
    #         symbol.session = session

    #     self.create_connection()

    #     # Start the receive thread
    #     receive_thread = threading.Thread(target=receive_thread)
    #     # Set as a daemon thread to exit when the main program exits
    #     receive_thread.daemon = True
    #     receive_thread.start()

    #     # Then send a message through the tunnel
    #     messages = []
    #     for symbol in symbols:
    #         messages.append(["chart_create_session", [chart_session, ""]])
    #     messages.append(["quote_create_session", [session]])
    #     data = "={\"adjustment\":\"splits\",\"session\":\"extended\",\"settlement-as-close\":false,\"symbol\":\"" + symbol_id + "\"}"
    #     messages.append(["quote_add_symbols", [session, data]])
    #     messages.append(["resolve_symbol", [
    #         chart_session,
    #         "sds_sym_1",
    #         data
    #     ]])
    #     messages.append(["create_series", [
    #         chart_session, "sds_1", "s1", "sds_sym_1", "1S", 300, ""
    #     ]])
    #     messages.append(["quote_set_fields", [
    #         session,
    #         "ch",
    #         "chp",
    #         "current_session",
    #         "description",
    #         "local_description",
    #         "language",
    #         "exc hange",
    #         "fractional",
    #         "is_tradable",
    #         "lp",
    #         "lp_time",
    #         "minmov",
    #         "minmove2",
    #         "original_name",
    #         "pricescale",
    #         "pro_name",
    #         "short_name",
    #         "type",
    #         "update_mode",
    #         "volume",
    #         "currency_code",
    #         "rchp",
    #         "rtc"
    #     ]])
    #     messages.append(["quote_add_symbols", [session, symbol_id]])
    #     messages.append(["quote_fast_symbols", [session, data]])
    #     messages.append(["quote_fast_symbols", [session, symbol_id]])
    #     temp = "={\"symbol\":\"" + symbol_id + \
    #         "\",\"adjustment\":\"splits\",\"session\":\"extended\"}"
    #     messages.append(["resolve_symbol", [
    #         chart_session, "symbol_1", temp
    #     ]])
    #     messages.append(["request_more_tickmarks", [
    #         chart_session,
    #         "sds_1",
    #         10
    #     ]])
    #     messages.append(["request_more_data", [
    #         chart_session,
    #         "sds_1",
    #         100
    #     ]])
    #     while True:
    #         try:
    #             for mess in messages:
    #                 self.send_message(self.ws, mess[0], mess[1])
    #                 time.sleep(0.2)
    #             messages = []
    #             time.sleep(0.5)
    #         except KeyboardInterrupt:
    #             break
    #         except Exception as e:
    #             print("=========except", datetime.now(), e)
    #             if ('closed' in str(e) or 'lost' in str(e)):
    #                 print("=========try")
    #                 self.realtime_bar_chart(5, 1, callback)
