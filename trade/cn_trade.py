# -*- coding: utf-8 -*
from util import *
import datetime
import time

class CNTrade(object):
    def __init__(self, p):
        # self.email = Email()
        self.client = client(host="127.0.0.1")
        self.p_path = os.path.dirname(os.path.abspath(__file__)) + '/config/'+p+'.json'
        self.portfolio_list = helpers.file2dict(self.p_path)
        # 每日更新
        self.last_trade_time = get_trade_date_series("CN")  # 最近一个交易日的开始时间
        # self.trade_time = get_date_now("CN")  # 被last_trade_time替代
        self.is_update_stocks = False # 更新市场数据
        self.is_update_ports = False # 更新组合消息（df,wb）
        self.is_report = False  # 每日汇报
        self.all_stocks_data = None # 市场数据集合
        self.is_ipo = False # 每天ipo记录

    def update_para(self, TEST_STATE):
        """
        当每天自动运行到固定时间更新，否则启动时候更新
        :return:
        """
        now_time = datetime.datetime.now()
        update_begin_1 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 27, 30)
        update_begin_2 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 27, 50)
        if update_begin_1 < now_time < update_begin_2:
            self.last_trade_time = get_trade_date_series("CN")
            if is_trade_time(TEST_STATE, self.last_trade_time):
                self.is_update_stocks = False
                self.all_stocks_data = None
                self.is_update_ports = False
                self.is_report = False
                self.is_ipo = False
        time.sleep(6)

    def trade_yjb(self, dif, code, price, amount, enable_amount):
        """
         下单
        :param dif:
        :param code:
        :param price:
        :param amount:
        :param enable_amount:
        :return:
        """
        result = {}
        if dif > 0:
                if amount >= 100:
                    result = str_to_dict(self.client.exec_order("buy " + code + " " + str(price) + " " + str(amount)))
                    result["trade"] = "买入 "+code+" @ " + str(price) + " 共 " + str(amount)
                else:
                    result["trade"] = "买入不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
        elif dif < 0:
            amount = enable_amount if dif == -2 else min(enable_amount, amount)
            if amount >= 100:
                result = str_to_dict(self.client.exec_order("sell " + code + " " + str(price) + " " + str(amount)))
                result["trade"] = "卖出 "+code+" @ " + str(price) + " 共 " + str(amount)
            else:
                result["trade"] = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
        elif dif == 0:
            result["trade"] = code + " 数量为0，不动！"

        result = result["error_info"] + result["trade"] if "error_info" in result else result["trade"]
        return result

    def trade(self, dif, code, price, amount, enable_amount):
        """
         下单
        :param dif:
        :param code:
        :param price:
        :param amount:
        :param enable_amount:
        :return:
        """
        result = {}
        result["status"] = "OK"

        if code[0] == "5":
            result["trade"] = "暂时不支持操作 " + code

        else:
            if dif > 0:
                    if amount >= 100:
                        result["status"] = self.client.exec_order("buy " + code + " " + str(price) + " " + str(amount))
                        result["trade"] = "买入 "+code+" @ " + str(price) + " 共 " + str(amount)
                    else:
                        result["trade"] = "买入不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
            elif dif < 0:
                amount = enable_amount if dif == -2 else min(enable_amount, amount)
                if amount >= 100:
                    result["status"] = self.client.exec_order("sell " + code + " " + str(price) + " " + str(amount))
                    result["trade"] = "卖出 "+code+" @ " + str(price) + " 共 " + str(amount)
                else:
                    result["trade"] = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
            elif dif == 0:
                result["trade"] = code + " 数量为0，不动！"

        result = result["status"] + " " + result["trade"] if result["status"] != "OK" else result["trade"]

        return result