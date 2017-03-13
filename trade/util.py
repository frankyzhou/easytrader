# -*- coding: utf-8 -*-
import tushare as ts
import logging, logging.handlers
from HTMLParser import HTMLParser
from easytrader.MongoDB import *
from yahoo_finance import Share
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
import socket
from decimal import Decimal
import ast
import re
from easytrader.log import log
from PIL import Image
import pytesseract


def is_today(report_time, last_trade_time):
    report_time = datetime.datetime.strptime(report_time,"%Y-%m-%d %H:%M:%S")
    if report_time > last_trade_time:
        return True
    else:
        return False


def get_price_by_factor(all_stocks_data, code, price, factor):
    price = get_four_five(price*factor, 2)
    try:
        stock = all_stocks_data[all_stocks_data.code == code]
        values = stock.settlement.values
        close_last = float(values)
        point = 0.1
        high_stop = get_four_five(close_last * (1+point), 2)
        low_stop = get_four_five(close_last * (1-point), 2)
        if factor > 1:
            price = min(price, high_stop)
        else:
            price = max(price, low_stop)
    except Exception, e:
        print e
        print values
        print len(values)

    return price


def get_four_five(num, pre=3):
    p = '{:.' + str(pre) + 'f}'
    return float(p.format(Decimal(num)))


# def get_date_now(country):
#     """
#     获得相应市场的每天交易岂止时间，上午开始，结束，下午开始，结束
#     :param country:
#     :return:
#     """
#     now_time = datetime.datetime.now()
#     if country == "CN":
#         # 开盘提前更新数据
#         trade_begin_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 28, 0)
#         trade_end_am = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 11, 30, 0)
#         trade_begin_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 13, 0, 0)
#         trade_end_pm = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 15, 0, 0)
#
#     elif country == "US":
#         offsize = 0 if now_time.hour < 4 else 1
#         base_time = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day))
#         trade_begin_am = base_time + datetime.timedelta(days=offsize-1, hours=21, minutes=25)
#         trade_end_pm = base_time + datetime.timedelta(days=offsize, hours=4, minutes=5)
#         trade_end_am = base_time + datetime.timedelta(days=offsize)
#         trade_begin_pm = trade_end_am
#
#     return [trade_begin_am, trade_end_am, trade_begin_pm, trade_end_pm]


def is_trade_time(test, trade_time):
    """
    判断当前时间是否为交易时间
    :param test: 测试
    :param trade_time: get_tradetime_series[0]而来
    :return:
    """
    now_time = datetime.datetime.now()
    if test: return True

    if trade_time[0] <= now_time <= trade_time[1] \
            or trade_time[2] <= now_time <= trade_time[3]:
        return True
    else:
        return False


def get_trade_date_series(country):
    """
    获得相应市场最近一个交易日的开始时间
    :param country:
    :return:
    """
    if country == "CN":
        df = ts.get_realtime_quotes("sh")
        date_cn = datetime.datetime.strptime(df["date"].values[0].encode("utf8"), "%Y-%m-%d")
        trade_begin_am = datetime.datetime(int(date_cn.year), int(date_cn.month), int(date_cn.day), 9, 25, 0)
        trade_end_am = datetime.datetime(int(date_cn.year), int(date_cn.month), int(date_cn.day), 11, 30, 0)
        trade_begin_pm = datetime.datetime(int(date_cn.year), int(date_cn.month), int(date_cn.day), 13, 0, 0)
        trade_end_pm = datetime.datetime(int(date_cn.year), int(date_cn.month), int(date_cn.day), 15, 0, 0)

    elif country == "US":
        yahoo = Share('QQQ')
        time_str = yahoo.get_trade_datetime()
        base_time = datetime.datetime.strptime(time_str[:10], "%Y-%m-%d")
        # offsize = 0 if now_time.hour < 4 else 1
        # base_time = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day))
        trade_begin_am = base_time
        trade_end_pm = base_time + datetime.timedelta(hours=3)
        trade_end_am = base_time + datetime.timedelta(hours=6)
        trade_begin_pm = trade_end_am

    return [trade_begin_am, trade_end_am, trade_begin_pm, trade_end_pm]


def get_logger(collection, name=None, is_first=True):
    time = datetime.datetime.now().strftime("%Y-%m-%d")
    name = "-" + name if name else ""
    logfile = '../logs/' + collection + "/" + time + name + '.log'

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=logfile,
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    if is_first:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

    logger = logging.getLogger(collection)
    return logger


def record_msg(logger, msg, subject=None, email=None):
    if type(msg).__name__ != "unicode":
        msg = unicode(msg, "utf-8")
    logger.info(msg)
    if email:
        email.send_email(msg, subject)


def get_server(host='', port=51500):
    # host = '' # Bind to all interfaces
    # port = 51500
    # Step1: 创建socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Step2: 设置socket选项(可选)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Step3: 绑定到某一个端口
    s.bind((host, port))
    return s


def update_stocks_data(state, all_stocks):
    """
    通过tushare获取全市场开盘情况
    :param state:
    :param all_stocks:
    :return:
    """
    if not state:
        try:
            all_stocks = ts.get_today_all()
            state = True
            print "\n" + "-" * 50
            log.info("updates stock data!")
        except Exception, e:
            print e
            all_stocks = None
            state = False
    return state, all_stocks


def str_to_dict(string):
    return ast.literal_eval(string)


def cal_time_cost(begin):
    try:
        dt_begin = datetime.datetime.strptime(begin, "%Y-%m-%d %H:%M:%S")
    except:
        dt_begin = datetime.datetime.strptime(begin, "%Y-%m-%d %H:%M")
    return str((datetime.datetime.now() - dt_begin).seconds)


def parse_digit(string):
    p = re.compile(r"\d+\.*\d*")
    m = p.findall(string)
    return float(m[0]), float(m[1]), float(m[2])


# def is_trade_day(last_trade_time):
#     """
#     判断当天是否为交易日，
#     :param last_trade_time: get_trade_date_series得到的最近一个交易日的开始时间
#     :return:
#     """
#     now = datetime.datetime.now()
#     return now.month == last_trade_time.month and now.day == last_trade_time.day


def get_client(host='127.0.0.1', textport=51500, timeout=15):
    # 如果超时一般都是交易端有故障，抛出异常，邮件提示
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        port = int(textport)
    except ValueError:
        port = socket.getservbyname(textport, 'udp')
    s.connect((host, port))
    s.settimeout(timeout)
    return s


def get_code_name(all_data, code, name=None):
    n = all_data[["code", "name"]]
    try:
        if name:
            return n[n.name == name].values[0][0]
        else:
            return n[n.code == code].values[0][1]
    except Exception, e:
        print e
        return code if not name else name


class client:
    def __init__(self, host):
        self.client = get_client(host=host)

    def exec_order(self, order, response=True):
        self.client.sendall(order)
        if not response:
            return
        buf = self.client.recv(204800)
        if not len(buf):
            return "No data"
        return str(buf)


class MyHTMLParser(HTMLParser):
    def __init__(self):
      self.data=[]
      self.rt=0
      self.sy=0
      self.td=0
      self.mt=0
      self.linkname=''
      HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            for name, value in attrs:
                if name == "content" and "雪球" in value  and self.mt == 0:
                    self.data.append(value.split(" ")[0])
                    self.mt = 1
                    # return

        if tag == 'div':
            for name, value in attrs:
                if value == 'column-rt':
                    self.rt = 1
                    # return
                if value == 'stock-symbol':
                    self.sy = 1
                    # return

        if tag == 'td':
            self.td = 1
            # return

    def handle_data(self, data):
        if self.rt or self.sy or self.td or self.mt:
            self.linkname += data

    def handle_endtag(self, tag):
        if tag == 'div' or tag == 'td':
            # self.linkname=''.join(self.linkname.split())
            if self.rt or self.sy or self.td:
                self.linkname = self.linkname.strip()
                if self.linkname:
                    self.data.append(self.linkname)
                self.linkname = ''
                self.rt = 0
                self.sy = 0
                self.td = 0

    def getresult(self):
        data = self.data
        info_list = []
        # time = data[1][:-2]
        num = len(data)/6
        info_list.append(data[0])
        for i in range(0,num):
            e = {}
            stock = {"price":data[i*6+6], "reason":data[i*6+8]}
            stock_name = data[i*6+4]
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
    config_path = os.path.dirname(__file__) + '/config/email.json'
    
    def __init__(self):
        self.read_config(self.config_path)
        self.mail_host = self.account_config["mail_host"]  #设置服务器
        self.mail_user = self.account_config["mail_user"]   #用户名
        self.mail_pass = self.account_config["mail_pass"]   #口令
        self.mail_loca = self.account_config["mail_loca"]
        self.smtpObj = smtplib.SMTP()

    def read_config(self, path):
        self.account_config = helpers.file2dict(path)

    def send_email(self, msg, subject=None):
        # 第三方 SMTP 服务
        msgRoot = MIMEMultipart('related')  # root as base
        msgRoot['From'] = self.mail_loca + "_" + "stock@163.com"
        msgRoot['To'] = self.mail_user

        subject = subject if subject else msg
        msgRoot['Subject'] = Header(subject, 'utf-8')

        if subject == "ipo":
            # 发照片
            name = 'ipo/' + datetime.datetime.now().strftime("%Y-%m-%d") +".png"
            fp = open(name, 'rb')
            msgImage = MIMEImage(fp.read())
            fp.close()
            msgRoot.attach(msgImage)
            # 发文字
            msg = pytesseract.image_to_string(Image.open(name), lang="chi_sim")  # 覆盖原先文字

        message = MIMEText(msg, 'plain', 'utf-8')  # text
        msgRoot.attach(message)
        while 1:
            try:
                self.smtpObj.sendmail(self.mail_user, self.mail_user, msgRoot.as_string())
                # self.smtpObj.sendmail(self.mail_user, self.mail_user, message.as_string())
                # print "邮件发送成功"
                return
            except smtplib.SMTPException, ex:
                # print "Error: 无法发送邮件"
                self.smtpObj = smtplib.SMTP()
                self.smtpObj.connect(self.mail_host, 25)
                self.smtpObj.login(self.mail_user, self.mail_pass)
                print ex


# is_trade_time()
# get_trade_date_series()
# a = PorfolioPosition("Positions", "IB")
# # b = a.read_position("Positions", "IB")
# c = a.get_position_by_stock('ZH776826', "DUST")
# a.write_position("IB")
# print c
e = Email()
# # while True:
# # time.sleep(60*10)
e.send_email("ipo", "ipo")

