# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'

import datetime
import tushare as ts
import logging
import logging.handlers
from HTMLParser import HTMLParser

# after the last trade day
def is_today(report_time, last_trade_time):
    report_time = datetime.datetime.strptime(report_time,"%Y-%m-%d %H:%M:%S")
    last_trade_time = datetime.datetime.strptime(last_trade_time,"%Y-%m-%d")
    if report_time > last_trade_time:
        return True
    else:
        return False

def get_price_by_factor(price, factor):
    return round(price*factor, 2)

def is_trade_time():
    now_time = datetime.datetime.now()
    trade_begin_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 25, 0)
    trade_begin_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 12, 55, 0)
    trade_end_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 12, 35, 0)
    trade_end_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 23, 05, 0)

    if trade_begin_am < now_time < trade_end_am or trade_begin_pm < now_time < trade_end_pm:
        return True
    else:
        return False

def get_trade_date_series():
    # get the data of 000001 by tushare
    now = datetime.datetime.today()
    before = now - datetime.timedelta(days=30)
    start = before.strftime("%Y-%m-%d")
    end = now.strftime("%Y-%m-%d")
    df = ts.get_hist_data(code='sh', start=start, end=end)
    return df.index.values[0]

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
# is_trade_time()
# get_trade_date_series()

