# -*- coding: utf-8 -*-
import easytrader
import pandas as pd
import numpy as np
import time
from util import *
import sys

YEAR_TRADE_DAYS = 252
unrisk_rate = 0.025
COLLECTION = "seek_alpha"
portfolio_list = {
    'ZH847759':#黄金黄金
       {
            "percent": 0.2,
            "factor": 0.008,
            "name": "黄金黄金"
        }
}


def get_annualized_returns(profit_list):
    """
    计算收益的年化值
    :param profit_list:
    :return:
    """
    total_profit = profit_list[-1:]["value"].values[0] - 1
    annua_profit = total_profit / profit_list.index.size * YEAR_TRADE_DAYS
    return annua_profit


def analyse_profit(profit_list):
    """
    提取原数据成Dataframe，其中有date时间，daily每日收益，和value总价值（归一）
    :param profit_list:
    :return:
    """
    data = {'date': [], 'daily': [], 'value': []}
    for e in profit_list:
        data["date"].append(datetime.datetime.strptime(e["date"], "%Y-%m-%d"))
        data["value"].append(1 + e["percent"]/100)
        if len(data["daily"]) == 0:
            data["daily"].append(e["percent"]/100)
        else:
            data["daily"].append(data["value"][-1] - data["value"][-2])
    a = pd.DataFrame(data, columns=['date', 'daily', 'value'])
    return a


def get_cov(a, b):
    """
    获取a,b的协方差，取（0，1）或者（1，0）
    :param a:
    :param b:
    :return:
    """
    size = min(a.size, b.size)
    r = np.cov(a[-size:], b[-size:])
    r = r[0][1]
    return r


def get_volatility(p):
    """对中国股票市场而言，月标准差为日标准差乘以根号20；
    年标准差为日标准差乘以根号240.按照实际交易日来计算而不是日历时间来计算"""
    return np.std(p) * np.sqrt(YEAR_TRADE_DAYS)


class GetAlpha:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq2.json')

    def get_para_by_portfolio(self, p_name):
        self.xq.set_attr("portfolio_code", p_name)
        time.sleep(1)
        p, b = self.xq.get_profit_daily()
        if p and b:
            p, b = analyse_profit(p), analyse_profit(b)
            p_annua_profit = get_annualized_returns(p)
            b_annua_profit = get_annualized_returns(b)
            cov = get_cov(p["daily"].values, b["daily"].values)
            beta = cov / np.var(b["daily"].values)  #方差
            alpha = p_annua_profit - (unrisk_rate + beta * (b_annua_profit - unrisk_rate))
            volatility = get_volatility(p["daily"].values)
            sharp = (p_annua_profit - unrisk_rate) / volatility
            print portfolio_list[p_name]["name"] + ": alpha:" + str(alpha) + " beta:" + str(beta) + \
                  " sharp:" + str(sharp) + " volatility:" + str(volatility)

    def main(self, s, e):
        self.logger = get_logger(COLLECTION, name=str(s+"-"+e))
        s = int(s)
        e = int(e)
        tmp = s
        try:
            for no in range(s, e):
                tmp = no
                p_name = "ZH" + '{:0>6}'.format(no)
                self.xq.set_attr("portfolio_code", p_name)
                p, b = self.xq.get_profit_daily()
                if p and b:
                    if len(p) > 0 and len(b) > 0:
                        p, b = analyse_profit(p), analyse_profit(b)
                        p_annua_profit = get_annualized_returns(p)
                        b_annua_profit = get_annualized_returns(b)
                        cov = get_cov(p["daily"].values, b["daily"].values)
                        beta = cov / np.var(b["daily"].values)  #方差
                        alpha = p_annua_profit - (unrisk_rate + beta * (b_annua_profit - unrisk_rate))
                        volatility = get_volatility(p["daily"].values)
                        sharp = (p_annua_profit - unrisk_rate) / volatility
                        if alpha > 0 and sharp > 0:
                            record_msg(self.logger, p_name + ": alpha:" + str(alpha) + " beta:" + str(beta) +\
                                       " sharp:" + str(sharp) + " volatility:" + str(volatility))
        except Exception, e:
            print e
            return tmp - 1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: python get_alpha.py startNo endNo"
        exit(-1)

    end = sys.argv[2]
    start = sys.argv[1]

    while 1:
        if start:
            alpha = GetAlpha()
            start = alpha.main(start, end)
            time.sleep(60*10)
        else:
            break
    # for p in portfolio_list:
        # a.get_para_by_portfolio(p)
