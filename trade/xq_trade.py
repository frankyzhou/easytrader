# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import easytrader
from trade.util import *
import time

# declare basic vars
TEST_STATE = True
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"
SLIP_POINT = 0.01

portfolio_list ={
    'ZH016097':
        {
            "percent": 0.15,
            "factor": 0.01,
            "name": "绝对模拟"
        },
    'ZH000893':
        {
            "percent": 1.0,
            "factor": 0.003,
            "name": "成长投资组合"
         },
    'ZH743053':
        {
            "percent": 0.15,
            "factor": 0.003,
            "name": "我爱新能源"
         },
    'ZH226990':
        {
            "percent": 0.15,
            "factor": 0.003,
            "name": "雨后彩虹"
         }
}

class xq_trade:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.logger = get_logger(COLLECTION)
        self.db = MongoDB(XUEQIU_DB_NAME)
        self.last_trade_time = get_trade_date_series("CN")
        self.trade_time = get_date_now("CN")
        self.email = Email()

    def trade_by_entrust(self, entrust, k, factor, percent):
        for trade in entrust:
            # if not is_today(trade["report_time"], self.last_trade_time) or self.db.get_doc(COLLECTION, trade):
            #     break
            if self.db.get_doc(COLLECTION, trade):
                pass
            else:
                """only if entrust is today or not finished by no trade time"""
                position_yjb = self.yjb.get_position()
                balance = self.yjb.get_balance()[0]
                asset = balance["asset_balance"]
                trade["portfolio"] = k

                record_msg(logger=self.logger, msg="-"*50 + "\n" + k + " updates new operation!")

                code = str(trade["stock_code"][2:])
                price = get_price_by_factor(trade["business_price"], (1+factor))
                target_percent = trade["target_weight"] * percent /100 if trade["target_weight"] > 2.0 else 0.0

                '''before_percent has two version.  1.the position is caled by yjb;  2,the position is caled by xq; 已经有比例，故其他需要对应'''
                before_percent_yjb = self.yjb.get_position_by_stock(code, position_yjb, asset)
                before_percent_xq = trade["prev_weight"] * percent /100 if trade["prev_weight"] > 2.0 else 0.0
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
                code = "600037"
                dif = -0.04
                price = 14.74'''
                volume = dif*asset
                factor = factor if dif > 0 else -factor
                price = get_price_by_factor(trade["business_price"], (1+factor))
                result = {}
                amount = abs(volume) * (1+SLIP_POINT) // price // 100 * 100

                if dif > 0:
                    if amount >= 100:
                        result = self.yjb.buy(stock_code=code, price=price, amount=amount)
                        result["trade"] = "买入 "+code+" @ " + str(price) + " 共 " + str(amount)
                    else:
                        result["trade"] = "买入不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
                elif dif < 0:
                    if amount >= 100:
                        result = self.yjb.sell(stock_code=code, price=price, amount=amount)
                        result["trade"] = "卖出 "+code+" @ " + str(price) + " 共 " + str(amount)
                    else:
                        result["trade"] = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
                elif dif == 0:
                    result["trade"] = code + " 数量为0，不动！"

                result = result["error_info"] + result["trade"] if "error_info" in result else result["trade"]
                record_msg(logger=self.logger, msg=portfolio_list[k]["name"] + ": " + result)
                self.db.insert_doc(COLLECTION, trade)

    def main(self):
        while(1):
            if(is_trade_time(TEST_STATE, self.trade_time)):
            # judge whether it is trade time
                for k in portfolio_list.keys():
                    try:
                        self.xq.setattr("portfolio_code", k)
                        time.sleep(4)
                        entrust = self.xq.get_xq_entrust_checked()

                        factor = portfolio_list[k]["factor"]
                        percent = portfolio_list[k]["percent"]
                        self.trade_by_entrust(entrust, k, factor, percent)

                    except Exception, e:
                        msg = "xq:" + str(e.message)
                        record_msg(logger=self.logger, msg=msg, email=self.email)
                        return -1
                    #
                    #     time.sleep(30)
                    #     self.xq.autologin()

if __name__ == '__main__':
    xq = None
    while(1):
        # try:
            xq = xq_trade()
            xq.main()
            time.sleep(120)
        # except Exception, e:
        #     print e
        #     yjb.logger.info("outer: " + e.message)
        #     time.sleep(12)