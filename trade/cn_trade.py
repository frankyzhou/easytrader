# -*- coding: utf-8 -*
from util import *
import datetime


class CNTrade(object):
    def __init__(self):
        self.email = Email()
        self.client = client(host="10.104.236.87")
        # 每日更新
        self.last_trade_time = get_trade_date_series("CN")
        self.trade_time = get_date_now("CN")
        self.is_update_stocks = False
        self.is_update_ports = False
        self.all_stocks_data = None

    def update_para(self):
        """
        当每天自动运行到固定时间更新，否则启动时候更新
        :return:
        """
        now_time = datetime.datetime.now()
        update_begin_1 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 25, 30)
        update_begin_2 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 25, 35)
        if update_begin_1 < now_time < update_begin_2:
            self.last_trade_time = get_trade_date_series("CN")
            if is_trade_day(self.last_trade_time):
                self.trade_time = get_date_now("CN")
                self.is_update_stocks = False
                self.all_stocks_data = None

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