# coding: utf-8
from bs4 import BeautifulSoup
import helpers
from .webtrader import WebTrader
from .log import log
import time
import os
import requests
import json
import re
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import traceback
chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
# profile = "C:\Users\frankyzhou\AppData\Local\Google\Chrome\User Data\Profile 1"
# options = webdriver.ChromeOptions()
# options.add_argument("--user-data-dir=C:\Users\\frankyzhou\AppData\Local\Google\Chrome\User Data\Profile 1")
# options.add_argument('--profile-directory=Default')
# fp = webdriver.FirefoxProfile()

class WBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/wb.json'

    def __init__(self):
        super(WBTrader, self).__init__()
        self.portfolio = ""
        # self.account_config = {}
        self.request = requests
        self.multiple = 1000000
        # self.driver = webdriver.PhantomJS()
        self.home_list = []

    def login(self):
        self.driver = webdriver.Chrome(executable_path=chromedriver)
        # self.driver = webdriver.Firefox(executable_path="C:\Program Files (x86)\Mozilla Firefox\\browser\geckodriver.exe", firefox_profile=fp)
        try:
            self.driver.get("http://weibo.com/u/1880546295")
            time.sleep(10)
            self.driver.maximize_window()
            
            name_field = self.driver.find_element_by_id('loginname')
            name_field.clear()
            name_field.send_keys(self.account_config['account'])
            password_field = self.driver.find_element_by_name('password')
            password_field.clear()
            password_field.send_keys(self.account_config['password'])
            isLogged = False
            while not isLogged:
                try:
                    verify_pic = self.driver.find_element_by_xpath("//*[@id=\"pl_login_form\"]/div/div[3]/div[3]/a/img")
                    verify_pic.screenshot("login.png")
                    location = verify_pic.location  # 获取验证码x,y轴坐标
                    size = verify_pic.size  # 获取验证码的长宽
                    rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                              int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                    i = Image.open("login.png")  # 打开截图
                    frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                    frame4.save('vcode.jpg')
                    code = raw_input("please input vcode: ")
                except:
                    log.info("not verifycode in this page!")
                submit = self.driver.find_element_by_xpath("//*[@id=\"pl_login_form\"]/div/div[3]/div[6]/a")
                submit.click()
                if self.driver.title.find("我的首页") == 0:
                    isLogged = True
                    log.info("weibo has login!")
            self.driver.get("http://m.weibo.cn")
            time.sleep(5)
            return True
        except:
            traceback.print_exc()
            return False

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
        msg = self.get_json(self.config["entrust_prefix"] + self.get_attr("portfolio_code") +
                        self.config["entrust_fix"] + "1")
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
    
    def get_json(self, url, limit=3):
        times = 1
        while times < limit:
            self.driver.get(url)
            time.sleep(5)
            try:
                bsObj = BeautifulSoup(self.driver.page_source, "lxml")
                info_json = json.loads(bsObj.text)
                return info_json
            except:
                traceback.print_exc()
                self.login()
                times += 1
                time.sleep(10)
                
        return "wrong"
            









