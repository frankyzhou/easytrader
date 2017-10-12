# coding: utf-8
from bs4 import BeautifulSoup
from .webtrader import WebTrader
from .log import log
import time
import os
import json
import re
from selenium import webdriver
import traceback

chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument(r"user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")
# options.add_argument("user-data-dir=C:\Users\\frankyzhou\AppData\Local\Google\Chrome\User Data")

class DFTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/wb.json'

    def __init__(self):
        super(DFTrader, self).__init__()
        self.multiple = 1000000
        # self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)

    def login(self):
        self.driver.get("http://group.eastmoney.com/other,137596.html")
        time.sleep(6)
        self.driver.maximize_window()
        return True


    def update_driver(self, url, sec=10):
        self.driver.get(url)
        time.sleep(sec)

    def get_home(self):
        self.driver.get(self.config["portfolio"] + self.get_attr("portfolio_code"))
        # response = self.request.get(self.config["portfolio"] + self.get_attr("portfolio_code"))
        # bsObj = BeautifulSoup(self.driver.page_source, "lxml")
        # self.home_list = bsObj.findAll("div", {"class": "card card11 ctype-1"})
        # self.history_json = json.loads(response.text)

    def get_capital(self):
        info_json = self.get_json(self.config["portfolio"] + self.get_attr("portfolio_code"))
        # return float(p1.findall(self.home_list[1].text)[2]) * self.multiple
        return float(info_json["cards"][0]["card_group"][1]["group"][1]["item_title"]) * self.multiple

    def get_entrust(self):
        msg = self.driver.find_element_by_class_name("zuhe-cjtablediv").text.split("\n")
        entrust = []
        for e in msg:
            stock = {}
            tks = e.split()
            stock["report_time"] = tks[0] + " " + tks[1]
            stock["price"] = tks[5]
            stock["amount"] = tks[4][:-1]
            stock["stock_code"] = tks[3]
            stock["trade_type"] = tks[2]
            entrust.append(stock)
        return entrust











