# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'

import easytrader
import pandas as pd
import datetime
import numpy as np
import time
from util import *

YEAR_TRADE_DAYS = 252
unrisk_rate = 0.025
COLLECTION = "seek_alpha"
portfolio_list ={
    'ZH000893':#成长投资组合
        {"percent":0.4,
        "factor":0,
         },
    'ZH278165':#次新股副班长
        {"percent":0.33,
        "factor":0,
         },
    'ZH743053':#我爱新能源
        {"percent":0.34,
        "factor":0,
         },
    'ZH016097':#绝对模拟
       {"percent":0.2,
       "factor":0.008,
        },
    'ZH401833':#叫板瑞鹤仙
    {"percent":0.33,
    "factor":0,
     },
}
class get_alpha:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        self.logger = get_logger(COLLECTION)

    def get_annualized_returns(self, profit_list):
        """计算收益的年化值"""
        total_profit = profit_list[-1:]["value"].values[0] -1
        annua_profit = total_profit / profit_list.index.size * YEAR_TRADE_DAYS
        return annua_profit

    def analyse_profit(self, profit_list):
        """提取原数据成Dataframe，其中有date时间，daily每日收益，和value总价值（归一）"""
        data = {'date':[],'daily':[],'value':[]}
        for e in profit_list:
            data["date"].append(datetime.datetime.strptime(e["date"], "%Y-%m-%d"))
            data["value"].append(1 + e["percent"]/100)
            if len(data["daily"]) == 0:
                data["daily"].append(e["percent"]/100)
            else:
                data["daily"].append(data["value"][-1] - data["value"][-2])
        a = pd.DataFrame(data, columns=['date', 'daily', 'value'])
        return a

    def get_cov(self, a, b):
        """获取a,b的协方差，取（0，1）或者（1，0）"""
        size = min(a.size, b.size)
        r = np.cov(a[-size:], b[-size:])
        r = r[0][1]
        return r

    def get_volatility(self, p):
        """对中国股票市场而言，月标准差为日标准差乘以根号20；
        年标准差为日标准差乘以根号240.按照实际交易日来计算而不是日历时间来计算"""
        return np.std(p) * np.sqrt(YEAR_TRADE_DAYS)


    def main(self):
        for no in range(999999):
            p_name = "ZH" + '{:0>6}'.format(no)
            self.xq.setattr("portfolio_code", p_name)
            # time.sleep(3)
            p, b = self.xq.get_profit_daily()
            if p != None and b !=None:
                p, b = self.analyse_profit(p), self.analyse_profit(b)
                p_annua_profit = self.get_annualized_returns(p)
                b_annua_profit = self.get_annualized_returns(b)
                cov = self.get_cov(p["daily"].values, b["daily"].values)
                beta = cov / np.var(b["daily"].values)  #方差
                alpha = p_annua_profit - (unrisk_rate + beta * (b_annua_profit - unrisk_rate))
                volatility = self.get_volatility(p["daily"].values)
                sharp = (p_annua_profit - unrisk_rate) / volatility
                # if alpha >1 and sharp > 2:
                record_msg(self.logger, p_name + ": alpha:" + str(alpha) + " beta:" + str(beta) + " sharp:" + str(sharp))

if __name__ == '__main__':
    a = get_alpha()
    a.main()