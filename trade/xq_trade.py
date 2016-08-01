# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import easytrader
from trade.util import *
import time, re

# declare basic vars
TEST_STATE = True
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"
SLIP_POINT = 0

portfolio_list ={
    # 'ZH000893':
    #     {
    #         "percent": 0.8,
    #         "factor": 0.005,
    #         "name": "成长投资组合"
    #      },
    # 'ZH866987':
    #     {
    #         "percent": 0.3,
    #         "factor": 0.005,
    #         "name": "老高-再次翱翔"
    #      },
    # 'ZH006428':
    #     {
    #         "percent": 0.15,
    #         "factor": 0.005,
    #         "name": "跟票输光光"
    #      },
    # 'ZH182820':
    #     {
    #         "percent": 0.3,
    #         "factor": 0.005,
    #         "name": "晶核之王"
    #      },
    # 'ZH743053':
    #     {
    #         "percent": 0.3,
    #         "factor": 0.005,
    #         "name": "我爱新能源"
    #      },
    # 'ZH226990':
    #     {
    #         "percent": 0.15,
    #         "factor": 0.005,
    #         "name": "雨后彩虹"
    #      },
    'ZH016097':
        {
            "percent": 0.2,
            "factor": 0.02,
            "name": "绝对模拟"
        },
}

class xq_trade:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        # self.yjb = easytrader.use('yjb')
        # self.yjb.prepare('config/yjb.json')
        self.logger = get_logger(COLLECTION)
        self.db = MongoDB(XUEQIU_DB_NAME)
        self.last_trade_time = get_trade_date_series("CN")
        self.trade_time = get_date_now("CN")
        self.email = Email()
        self.is_update_stocks = False
        self.all_stocks_data = None
        self.client = client()

    def trade_by_entrust(self, entrust, k, factor, percent):
        for trade in entrust:
            # only if entrust is today or not finished by no trade time
            if not TEST_STATE:
                if not is_today(trade["report_time"], self.last_trade_time) or self.db.get_doc(COLLECTION, trade):
                    break
            else:
                if self.db.get_doc(COLLECTION, trade):
                    continue

            trade["portfolio"] = k
            record_msg(logger=self.logger, msg="-"*50 + "\n" + k + " updates new operation!")
            code = str(trade["stock_code"][2:])
            target_percent = trade["target_weight"] * percent /100 if trade["target_weight"] > 2.0 else 0.0
            """
            before_percent has two version.
            1.the position is caled by yjb;
            2,the position is caled by xq;
            已经有比例，故其他需要对应
            """
            before_percent_yjb, enable_amount, asset = self.parse_digit(self.client.exec_order("get_position "+ code))
            before_percent_xq = trade["prev_weight"] * percent /100 if trade["prev_weight"] > 2.0 else 0.0
            dif, price, amount = self.get_trade_detail(target_percent, before_percent_xq, before_percent_yjb, asset, factor, code, trade)

            result = self.trade(dif, code, price,amount, enable_amount)
            record_msg(logger=self.logger, msg=portfolio_list[k]["name"] + ": " + result)
            self.db.insert_doc(COLLECTION, trade)

    def trade(self, dif, code, price, amount, enable_amount):
        result = {}
        if dif > 0:
                if amount >= 100:
                    # result = self.yjb.buy(stock_code=code, price=price, amount=amount)
                    result = str_to_dict(self.client.exec_order("buy " + code + " " + str(price) + " " + str(amount)))
                    result["trade"] = "买入 "+code+" @ " + str(price) + " 共 " + str(amount)
                else:
                    result["trade"] = "买入不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
        elif dif < 0:
            if amount >= 100:
                amount = min(enable_amount, amount)  #防止超出可用股数
                # result = self.yjb.sell(stock_code=code, price=price, amount=amount)
                result = str_to_dict(self.client.exec_order("buy " + code + " " + str(price) + " " + str(amount)))
                result["trade"] = "卖出 "+code+" @ " + str(price) + " 共 " + str(amount)
            else:
                result["trade"] = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
        elif dif == 0:
            result["trade"] = code + " 数量为0，不动！"

        result = result["error_info"] + result["trade"] if "error_info" in result else result["trade"]
        return result

    def get_trade_detail(self, target_percent, before_percent_xq, before_percent_yjb, asset, factor, code, trade):
        dif_xq = target_percent - before_percent_xq
        dif_yjb = target_percent - before_percent_yjb

        # dif = dif_xq if dif_xq > 0 else min(max(dif_xq, dif_yjb), 0)
        if dif_xq > 0:
            dif = dif_xq
        elif target_percent == 0:
            dif = dif_yjb
        else:
            dif = min(max(dif_xq, dif_yjb), 0)

        '''如果dif_xq为正，那幅度选择dif_xq，避免过高成本建仓；
        当dif_xq为负，
        若dif_yjb为正，说明目前账户持仓比雪球目标还低，出于风险考虑不加仓，dif取0；
        若dif_yib为负，择最大的变化，避免持有证券数量不够
        '''
        # code = "600037"
        # dif = -0.04
        # price = 14.74

        volume = dif*asset
        factor = abs(factor) if dif > 0.0 else -abs(factor)
        price = get_price_by_factor(self.all_stocks_data, code, trade["business_price"], (1+factor))
        amount = abs(volume) * (1+SLIP_POINT) // price // 100 * 100

        return dif, price, amount

    def parse_digit(self, string):
        p = re.compile(r"\d+\.*\d*")
        m = p.findall(string)
        return float(m[0]), float(m[1]), float(m[2])

    def main(self):
        while(1):
            if(is_trade_time(TEST_STATE, self.trade_time)):
                self.is_update_stocks, self.all_stocks_data = update_stocks_data(self.is_update_stocks, self.all_stocks_data)
                for k in portfolio_list.keys():
                    #try:
                        self.xq.setattr("portfolio_code", k)
                        time.sleep(7)
                        entrust = self.xq.get_xq_entrust_checked()

                        factor = portfolio_list[k]["factor"]
                        percent = portfolio_list[k]["percent"]
                        self.trade_by_entrust(entrust, k, factor, percent)

                    # except Exception, e:
                    #     msg = "xq:" + str(e.message)
                    #     record_msg(logger=self.logger, msg=msg, email=self.email)
                    #     return -1

if __name__ == '__main__':
    xq = None
    while(1):
        xq = xq_trade()
        xq.main()
        time.sleep(60)
