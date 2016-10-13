# coding: utf-8
from .webtrader import WebTrader
import time
import os
from bs4 import BeautifulSoup
import requests
import json
import re
import base64


def json_load_byteified(file_handle):
    return _byteify(json.load(file_handle, object_hook=_byteify), ignore_dicts=True)


def json_loads_byteified(json_text):
    return _byteify(json.loads(json_text, object_hook=_byteify), ignore_dicts=True)


def _byteify(data, ignore_dicts =False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {_byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()
                }
    # if it's anything else, return it in its original form
    return data


class WBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/wb.json'

    def __init__(self):
        super(WBTrader, self).__init__()
        self.driver = PhantomJS()
        self.portfolio = ""

        self.account_config = {}
        self.request = requests
        self.multiple = 1000000
        self.home_list = []

    def update_driver(self, url, sec=10):
        self.driver.get(url)
        time.sleep(sec)

    def get_home(self):
        # self.driver.get(self.config["portfolio"] + self.get_attr("portfolio_code"))
        response = self.request.get(self.config["portfolio"] + self.get_attr("portfolio_code"))
        # bsObj = BeautifulSoup(self.driver.page_source, "lxml")
        # self.home_list = bsObj.findAll("div", {"class": "card card11 ctype-1"})
        self.history_json = json.loads(response.text)

    def get_capital(self):
        self.get_home()
        p1 = re.compile(r"\d+\.\d+")
        return float(p1.findall(self.home_list[1].text)[2]) * self.multiple

    def get_entrust(self):
        response = self.request.get(self.config["entrust_prefix"] + self.get_attr("portfolio_code") +
                        self.config["entrust_fix"] + "1")
        msg = json_loads_byteified(response.text)
        entrust = msg["cards"][0]["card_group"]
        p1 = re.compile(r"\d+\-\d+\-\d+")
        p2 = re.compile(r"\d+\:\d+")
        p3 = re.compile(r"\d+\.\d+")
        p4 = re.compile(r"\d+")
        p5 = re.compile(u"[\u4e00-\u9fa5]+")

        change_time = p1.findall(entrust[0]["desc"])[0]
        del entrust[0]
        for e in entrust:
            e["report_time"] = change_time + " " + p2.findall(e["desc1"])[0] + ":00"
            e["price"] = float(p3.findall(e["desc2"])[0])
            e["amount"] = int(p4.findall(e["desc3"])[0])
            e["stock_code"] = p4.findall(e["title_sub"])[0]
            e["trade_type"] = re.findall(p5, e["desc2"].decode("utf8"))[0]
            for key in e.keys():
                if key not in ["report_time", "price", "amount", "stock_code", "trade_type"]:
                    del e[key]

        return entrust

    #def get_capital(self):









