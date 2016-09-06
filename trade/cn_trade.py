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
    
    def update_operation(self, p, code, volume):   
        """
        根据下单，更新仓位数据库信息
        :param position:数据库仓位数据信息
        :param p:组合名
        :param code:股票代码
        :param volume:交易量
        :return:
        """
        # 股票若在则交易量相加， 不再则直接使用该交易量，并初始化其仓位信息
        if code in self.position.position["portfolio"][p]["stock"].keys():
            volume_before = self.position.position["portfolio"][p]["stock"][code]["volume"]
            volume_now = volume_before + volume
        else:
            volume_now = volume
            self.position.position["portfolio"][p]["stock"][code] = {"volume": 0, "price": 0, "percent": 0}
    
        self.position.position["portfolio"][p]["stock"][code]["volume"] = volume_now
        
    def update_portfolio(self, position, asset):
        """
        更新仓位数据库信息
        :param position:券商真实仓位
        :param asset:总资产
        :param self.portfolio_list:初始组合列表
        :return:
        """
        # 组合原先全部空，初始化组合信息
        if "portfolio" not in self.position_db.position.keys():
            self.position_db.position["portfolio"] = {}
            for p in self.portfolio_list.keys():
                self.position_db.position["portfolio"][p] = {"stock": {}, "percent_now": 0, "percent_fixed": 0}
        # 对于新加的组合初始化
        for p in self.portfolio_list.keys():
            if p not in self.position_db.position["portfolio"].keys():
                self.position_db.position["portfolio"][p] = {"stock": {}, "percent_now": 0, "percent_fixed": 0}
        # 更新时间，资产
        self.position_db.position["asset"] = asset #更新总资产
        self.position_db.position["date"] = datetime.datetime.now() #更新操作时间
        # 转化股价成字典
        position_dict = {}
        for e in position:
            code = e[0]
            price = round(e[3], 2)
            position_dict[code] = price

        # 逐个组合更新价格
        for p in self.position_db.position["portfolio"]:
            for code in self.position_db.position["portfolio"][p]["stock"].keys():
                if self.position_db.position["portfolio"][p]["stock"][code]["volume"] == 0:
                    self.position_db.position["portfolio"][p]["stock"].pop(code)
                else:
                    self.position_db.position["portfolio"][p]["stock"][code]["price"] = position_dict[code] if code in position_dict else 0

        # 逐个组合更新比例
        need_delete = []
        for p in self.position_db.position["portfolio"]:
            if p in self.portfolio_list.keys(): #没有删除的组合
                sum_percent = 0
                for code in self.position_db.position["portfolio"][p]["stock"]:
                    price = self.position_db.position["portfolio"][p]["stock"][code]["price"]
                    volume = self.position_db.position["portfolio"][p]["stock"][code]["volume"]
                    self.position_db.position["portfolio"][p]["stock"][code]["percent"] = price * volume / asset
                    sum_percent += self.position_db.position["portfolio"][p]["stock"][code]["percent"]
                self.position_db.position["portfolio"][p]["percent_now"] = sum_percent
                self.position_db.position["portfolio"][p]["percent_fixed"] = self.portfolio_list[p]["percent"]
            else: #没有的组合进行数据库删除
                need_delete.append(p)

        if len(need_delete):
            for p in need_delete:
                self.position_db.position["portfolio"].pop(p)