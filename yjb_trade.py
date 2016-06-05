# -*- coding: utf-8 -*-

__author__ = 'frankyzhou'
import datetime

import time
import easytrader
from easytrader import MongoDB as DB
from util import *

# declare basic vars
TEST_STATE = False
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"
portfolio_list ={
    # 'ZH000893':#成长投资组合
    #     {"percent":0.4,
    #     "factor":0,
    #      },
    'ZH278165':#次新股副班长
        {"percent":0.33,
        "factor":0,
         },
    'ZH743053':#我爱新能源
        {"percent":0.34,
        "factor":0,
         },
    #'ZH016097':#绝对模拟
    #    {"percent":0.2,
    #    "factor":0.008,
    #     },
    'ZH401833':#叫板瑞鹤仙
    {"percent":0.33,
    "factor":0,
     },

}

class yjb_trade:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        self.yjb = easytrader.use('yjb')
        # self.yjb.prepare('yjb.json')
        self.logger = get_logger(COLLECTION)
        self.db = DB.get_mongodb(XUEQIU_DB_NAME)
        self.last_trade_time = get_trade_date_series()
        self.trade_time = get_date_now()

    def trade_by_entrust(self, entrust, k, factor, percent):
        for trade in entrust:
            # if not is_today(trade["report_time"], self.last_trade_time) or DB.get_doc(self.db, COLLECTION, trade):
            if DB.get_doc(self.db, COLLECTION, trade):
                break
            else:
                #  only if entrust is today or not finished by no trade time
                position_yjb = self.yjb.get_position()
                balance = self.yjb.get_balance()[0]
                asset = balance["asset_balance"]
                trade["portfolio"] = k

                self.logger.info("-"*50)
                print "-"*50
                self.logger.info(k + " update new operaion!")
                print k + " update new operaion!"

                code = str(trade["stock_code"][2:])
                price = trade["business_price"]
                # dif = trade['entrust_amount']/100

                target_percent = trade["target_weight"] * percent /100 if trade["target_weight"] > 2.0 else 0.0
                # before_percent has two version.
                # 1.the position is caled by yjb
                # 2,the position is caled by xq
                #已经有比例，故其他需要对应
                before_percent_yjb = self.yjb.get_position_by_stock(code, position_yjb, asset)
                before_percent_xq = trade["prev_weight"] * percent /100 if trade["prev_weight"] > 2.0 else 0.0
                dif_xq = target_percent - before_percent_xq
                dif_yjb = target_percent - before_percent_yjb

                dif = dif_xq if dif_xq > 0 else min(max(dif_xq, dif_yjb), 0)
                # 如果dif_xq为正，那幅度选择dif_xq，避免过高成本建仓；
                # 当dif_xq为负，
                # 若dif_yjb为正，说明目前账户持仓比雪球目标还低，出于风险考虑不加仓，dif取0；
                # 若dif_yib为负，择最大的变化，避免持有证券数量不够
                volume = dif*asset

                if dif > 0:
                    price = get_price_by_factor(price, (1+factor))
                    if volume/price >= 100:
                        result = self.yjb.buy(code, price, volume= volume)
                        self.logger.info("买入 "+code+" @ " + str(price) + " 共 " + str(volume))
                        print "买入 "+code+" @ " + str(price) + " 共 " + str(volume)
                    else:
                        self.logger.info("不足100股 "+code+" @ " + str(price) + " 共 " + str(volume))
                        result = "买入不足100股 "+code+" @ " + str(price) + " 共 " + str(volume)
                elif dif < 0:
                    volume = -volume
                    if volume/price >= 100:
                        result = self.yjb.sell(code, price, volume= volume)
                        self.logger.info("卖出 "+code+" @ " + str(price) + " 共 " + str(volume))
                        print "卖出 "+code+" @ " + str(price) + " 共 " + str(volume)
                    else:
                        self.logger.info("卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(volume))
                        result = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(volume)
                elif dif == 0:
                    result = code + " 数量为0，不动！"
                # out = ""
                # for key in result.keys():
                #     out = out + str(key) + " : " + str(result[key]) + " "
                result = result["error_info"] if "error_info" in result else result
                self.logger.info(result)
                print result
                DB.insert_doc(self.db, COLLECTION, trade)

    def main(self):
        while(1):
            if(is_trade_time(TEST_STATE, self.trade_time)):
            # judge whether it is trade time
                for k in portfolio_list.keys():
                    try:
                        self.xq.setattr("portfolio_code", k)
                        time.sleep(1)
                        entrust = self.xq.get_xq_entrust_checked()

                        factor = portfolio_list[k]["factor"]
                        percent = portfolio_list[k]["percent"]

                        self.trade_by_entrust(entrust, k, factor, percent)

                    except Exception, e:
                        print e
                        self.logger.info(e)

if __name__ == '__main__':
    while(1):
        try:
            yjb = yjb_trade()
            yjb.main()

        except Exception, e:
            print e
            yjb.logger.info(e)
            time.sleep(100)