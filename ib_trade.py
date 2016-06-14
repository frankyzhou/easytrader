# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'

import time
import easytrader
from easytrader.MongoDB import *
from util import *
from easytrader.ibtrader import IBWrapper, IBclient
from swigibpy import Contract as IBcontract

# declare basic vars
TEST_STATE = False
XUEQIU_DB_NAME = "Xueqiu"
IB_DB_NAME = "IB"
HISTORY_OPERATION_XQ = "USA_history_operation"
IB_POSITION = "Position"
IB_HISTORY = "History"

portfolio_list ={
    'ZH796463':#试一试
        {"percent":0.015,
        "factor":0,
         },
    'ZH776826':#2016商品抄底组合
        {"percent":0.015,
        "factor":0,
         },
    # 'ZH856129':#etf负向做空
    #     {"percent":0.008,
    #     "factor":0,
    #      },
    # 'ZH866458':#中国市场多空
    #     {"percent":0.008,
    #     "factor":0,
    #      },
}

class ib_trade:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        self.logger = get_logger(HISTORY_OPERATION_XQ)
        self.db_xq = MongoDB(XUEQIU_DB_NAME)
        # self.db_ib = MongoDB(IB_DB_NAME)
        self.last_trade_time = get_trade_date_series("US")
        self.trade_time = get_date_now("US")
        self.callback = IBWrapper()
        self.ibcontract = IBcontract()
        self.ibcontract.secType = "STK"
        self.ibcontract.exchange="SMART"
        self.ibcontract.currency="USD"
        self.client = IBclient(self.callback)
        self.position_ib = PorfolioPosition(IB_DB_NAME, IB_POSITION)

    def trade_by_entrust(self, entrust, k, factor, percent):
        for trade in entrust:
            msg = ""
            account_data = []
            position_ib = []
            # try:
            if not is_today(trade["report_time"], self.last_trade_time) or self.db_xq.get_doc(HISTORY_OPERATION_XQ, trade):
            # if self.db_xq.get_doc(HISTORY_OPERATION_XQ, trade):
                break
            else:
                #  only if entrust is today or not finished by no trade time
                del account_data[:]
                del position_ib[:]
                account_data, position_ib = self.client.get_IB_account_data()
                asset = float(account_data[31][1])
                self.client.update_portfolio(self.position_ib, position_ib, asset, portfolio_list)

                trade["portfolio"] = k
                self.logger.info("-"*50)
                print "-"*50
                self.logger.info(k + " update new operaion!")
                print k + " update new operaion!"

                code = str(trade["stock_code"])
                price = trade["business_price"]
                # dif = trade['entrust_amount']/100

                target_percent = trade["target_weight"] * percent /100 if trade["target_weight"] > 2.0 else 0.0
                # before_percent has two version.
                # 1.the position is caled by ib
                # 2,the position is caled by xq
                #已经有比例，故其他需要对应
                before_percent_xq = trade["prev_weight"] * percent /100 if trade["prev_weight"] > 2.0 else 0.0
                before_percent_ib, rest = self.client.get_position_by_stock(self.position_ib, code, asset, k)

                dif_xq = target_percent - before_percent_xq
                dif_ib = target_percent - before_percent_ib
                dif = max(min(dif_xq, rest), 0) if dif_xq > 0 else min(dif_ib, 0)
                # 如果dif_xq为正，
                    # 选择空余金额与需要金额中较小的，防止组合规模溢出。但也要防止出现负值。
                # 当dif_xq为负，
                    # 若dif_ib为正，说明目前账户持仓比雪球目标还低，出于风险考虑不加仓，dif取0；
                    # 若dif_ib为负，择dif_ib，将该组合下所有标的清仓
                turn_volume = dif*asset
                if dif != 0:
                    price = get_price_by_factor(price, (1+factor))
                    volume = int(turn_volume/price)
                    if abs(volume) >= 1:
                        self.ibcontract.symbol = code
                        orderid = self.client.place_new_IB_order(self.ibcontract, volume, price, "MKT", orderid=None)
                        if volume > 0:
                            msg = "买入 "+code+" @ " + str(price) + " 共 " + str(volume)
                        else:
                            msg = "卖出 "+code+" @ " + str(price) + " 共 " + str(-volume)
                        self.client.update_operation(self.position_ib, k, code, volume)
                    else:
                        msg = "不足1股 "+code+" @ " + str(price)
                elif dif == 0:
                    msg = code + " 数量为0，不动！"
        # except Exception, e:
        #     record_msg(self.logger, e)
        # finally:
            if len(msg) !=0:
                record_msg(self.logger, msg)
                self.position_ib.write_position(IB_POSITION)
                self.db_xq.insert_doc(HISTORY_OPERATION_XQ, trade)

    def main(self):
        while(1):
            if(is_trade_time(TEST_STATE, self.trade_time)):
            # judge whether it is trade time
                for k in portfolio_list.keys():
                    # try:
                    self.xq.setattr("portfolio_code", k)
                    time.sleep(1)
                    entrust = self.xq.get_xq_entrust_checked()

                    factor = portfolio_list[k]["factor"]
                    percent = portfolio_list[k]["percent"]

                    self.trade_by_entrust(entrust, k, factor, percent)
                    # except Exception, e:
                    #     print e
                    #     self.logger.info(e)
                    # self.position_ib.write_position(IB_POSITION)

if __name__ == '__main__':
    while(1):
        # try:
            ib = ib_trade()
            ib.main()
        # except Exception, e:
        #     print e
            # ib.logger.info(e)
            time.sleep(100)