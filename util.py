# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'

import tushare as ts
import logging
import logging.handlers
from HTMLParser import HTMLParser
from easytrader.MongoDB import *
from yahoo_finance import Share
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time
# after the last trade day
def is_today(report_time, last_trade_time):
    report_time = datetime.datetime.strptime(report_time,"%Y-%m-%d %H:%M:%S")
    if report_time > last_trade_time:
        return True
    else:
        return False

def get_price_by_factor(price, factor):
    return round(price*factor, 2)

def get_date_now(country):
    now_time = datetime.datetime.now()
    if country == "CN":
        trade_begin_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 20, 0)
        trade_end_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 15, 05, 0)
    elif country == "US":
        offsize = 0 if now_time.hour < 4 else 1
        trade_begin_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day)+offsize-1, 21, 25, 0)
        trade_end_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day)+offsize, 4, 05, 0)

    return [trade_begin_am, trade_end_pm]

def is_trade_time(test, trade_time):
    now_time = datetime.datetime.now()
    if test: return True

    if trade_time[0] < now_time < trade_time[1]:
        return True
    else:
        return False

def get_trade_date_series(country):
    # get the data of 000001 by tushare
    if country == "CN":
        now = datetime.datetime.today()
        before = now - datetime.timedelta(days=30)
        start = before.strftime("%Y-%m-%d")
        end = now.strftime("%Y-%m-%d")
        df = ts.get_hist_data(code='sh', start=start, end=end)
        date_cn = datetime.datetime.strptime(df.index.values[0],"%Y-%m-%d") + datetime.timedelta(hours=15, minutes=5)
        return date_cn

    elif country == "US":
        yahoo = Share('QQQ')
        time_str = yahoo.get_trade_datetime()
        date_us = datetime.datetime.strptime(time_str[:10], "%Y-%m-%d") + datetime.timedelta(hours=28, minutes=5)
        return date_us

def get_logger(COLLECTION):
    TIME = datetime.datetime.now().strftime("%Y-%m-%d")
    LOG_FILE = 'logs/' + TIME + COLLECTION +'.log'
    handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler

    fmt = '%(asctime)s -  %(message)s'
    formatter = logging.Formatter(fmt)   # 实例化formatter
    handler.setFormatter(formatter)      # 为handler添加formatter

    logger = logging.getLogger('tst')    # 获取名为tst的logger
    logger.addHandler(handler)           # 为logger添加handler
    logger.setLevel(logging.DEBUG)

    return logger

def record_msg(logger, email, msg):
    logger.info(msg)
    print msg
    email.send_email(msg)

class MyHTMLParser(HTMLParser):
    def __init__(self):
      self.data=[]
      self.rt=0
      self.sy=0
      self.td=0
      self.linkname=''
      HTMLParser.__init__(self)

    def handle_starttag(self,tag,attrs):
        if tag =='div':
            for name,value in attrs:
                if value == 'column-rt':
                    self.rt=1
                if value == 'stock-symbol':
                    self.sy=1
        if tag=='td':
            self.td=1

    def handle_data(self,data):
      if self.rt or self.sy or self.td:
          self.linkname+=data
    def handle_endtag(self,tag):
        if tag=='div' or tag=='td':
            # self.linkname=''.join(self.linkname.split())
            self.linkname=self.linkname.strip()
            if  self.linkname:
              self.data.append(self.linkname)
            self.linkname=''
            self.rt=0
            self.sy=0
            self.td=0

    def getresult(self):
        data = self.data
        info_list = []
        time = data[1][:-2]
        num = len(data)/6
        # dic["time"] = datetime.datetime.strptime(time, "%Y.%m.%d %H:%M")
        for i in range(0,num):
            e = {}
            stock = {"price":data[i*6+5], "reason":data[i*6+7]}
            stock_name = data[i*6+3]
            e[stock_name] = stock
            info_list.append(e)
        return info_list

class PorfolioPosition():
    def __init__(self, db, coll):
        # self.db_name = db
        # self.coll_name = coll
        self.db = MongoDB(db)
        self.coll = self.db.db[coll]
        self.read_position()

    def read_position(self):
        for a in self.coll.find():
            self.position = a
            return
        self.position = {"none":0}

    def write_position(self, coll):
        self.db.clear_all_datas(coll)
        self.db.insert_doc(coll, self.position)

    def get_position_by_stock(self, portfolio, code):
        if portfolio in self.position.keys():
            if code in self.position[portfolio]:
                return self.position[portfolio][code]

class Email():
    config_path = os.path.dirname(__file__) + '/easytrader/config/email.json'
    def __init__(self):
        self.read_config(self.config_path)
        self.mail_host = self.account_config["mail_host"]  #设置服务器
        self.mail_user = self.account_config["mail_user"]   #用户名
        self.mail_pass = self.account_config["mail_pass"]   #口令
        self.smtpObj = smtplib.SMTP()

    def read_config(self, path):
        self.account_config = helpers.file2dict(path)

    def send_email(self, msg):
        # 第三方 SMTP 服务
        message = MIMEText(msg, 'plain', 'utf-8')
        message['From'] = "stock@163.com"
        message['To'] =  "zlj"

        subject = msg
        message['Subject'] = Header(subject, 'utf-8')
        while(1):
            try:
                self.smtpObj.sendmail(self.mail_user, self.mail_user, message.as_string())
                # print "邮件发送成功"
                return
            except smtplib.SMTPException, ex:
                self.smtpObj.connect(self.mail_host, 25)
                self.smtpObj.login(self.mail_user, self.mail_pass)
                # print "Error: 无法发送邮件"
                print ex
# is_trade_time()
# get_trade_date_series()
# a = PorfolioPosition("Positions", "IB")
# # b = a.read_position("Positions", "IB")
# c = a.get_position_by_stock('ZH776826', "DUST")
# a.write_position("IB")
# print c
# e = Email()
# while True:
#     time.sleep(60*10)
#     e.send_email("i love you")
