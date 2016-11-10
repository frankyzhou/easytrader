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
options.add_argument("user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")
# options.add_argument("user-data-dir=C:\Users\\frankyzhou\AppData\Local\Google\Chrome\User Data")

class WBTrader(WebTrader):
    config_path = os.path.dirname(__file__) + '/config/wb.json'

    def __init__(self):
        super(WBTrader, self).__init__()
        self.multiple = 1000000
        # self.driver = webdriver.PhantomJS()
        self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
        # self.driver = webdriver.Firefox(executable_path="C:\Program Files (x86)\Mozilla Firefox\\browser\geckodriver.exe", firefox_profile=fp)

    def login(self):
        # isLogged = False
        #
        # while not isLogged:
            #try:
                self.driver.get("http://weibo.com/u/1880546295/home?topnav=1&wvr=6")
                time.sleep(6)
                self.driver.maximize_window()
                if self.driver.title.find("我的首页") == 0:
                    log.info("weibo has login!")
                else:
                    log.warn("need to login!")
                    raise Exception
                # login_field = self.driver.find_elements_by_link_text("登录")[0]
                # login_field.click()
                # time.sleep(5)
                # name_field = self.driver.find_elements_by_name("username")[2]
                # name_field.clear()
                # name_field.send_keys(self.account_config['account'])
                # password_field = self.driver.find_elements_by_name("password")[2]
                # password_field.clear()
                # password_field.send_keys(self.account_config['password'])

                # self.driver.save_screenshot("login.png")
                # location = verify_pic.location  # 获取验证码x,y轴坐标
                # size = verify_pic.size  # 获取验证码的长宽
                # rangle = (int(location['x']), int(location['y']), int(location['x'] + size['width']),
                #           int(location['y'] + size['height']))  # 写成我们需要截取的位置坐标
                # i = Image.open("login.png")  # 打开截图
                # frame4 = i.crop(rangle)  # 使用Image的crop函数，从截图中再次截取我们需要的区域
                # frame4.save('vcode.jpg')
                # code = raw_input("please input vcode: ")
                # verify_field = self.driver.find_element_by_name("verifycode")
                # verify_field.clear()
                # verify_field.send_keys(unicode(code))
            #except:
                # log.info("not verifycode in this page!")
                # submit = self.driver.find_element_by_class_name("W_btn_a")
                # submit.click()
                # time.sleep(20)

                self.driver.get("http://m.weibo.cn")
                time.sleep(5)
                return True
        # except:
        #     traceback.print_exc()
        #     return False

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
                if info_json["ok"] == 0:
                    raise Exception
                return info_json
            except:
                traceback.print_exc()
                log.warn("json not correct. try to relogin.")
                self.driver.save_screenshot("error.jpg")
                self.login()
                times += 1
                time.sleep(10)
                
        return "wrong"
            









