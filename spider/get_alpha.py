# -*- coding: utf-8 -*-
import easytrader
import pandas as pd
import numpy as np
import time
from trade.cn_trade import CNTrade
from trade.util import *
import sys
import traceback
# import matplotlib.pyplot as plt

TEST_STATE = False
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


def cal_volatility(p):
    """对中国股票市场而言，月标准差为日标准差乘以根号20；
    年标准差为日标准差乘以根号240.按照实际交易日来计算而不是日历时间来计算"""
    return np.std(p) * np.sqrt(YEAR_TRADE_DAYS)


def cal_max_drawdown(p_series):
    # fig = plt.figure()
    # p_series.plot()

    p = p_series.values
    cur_md = 0
    cur_mx = 0
    position = [0, 0]
    for i in range(len(p)):
        cur_mx = p[i] if p[i] > cur_mx else cur_mx
        # if p[i] > cur_mx:
        #     cur_mx = p[i]
        #     position[0] = i
        md = float(p[i] - cur_mx) / cur_mx
        cur_md = md if md < cur_md else cur_md
        # if md < cur_md:
        #     cur_md = md
        #     position[1] = i
    # plt.scatter(position[0], p[position[0]], edgecolors="red")
    # plt.scatter(position[1], p[position[1]], edgecolors="red")
    # fig.savefig("../logs/pic/" + p_name + ".jpg")
    return -cur_md


def cal_beta(p, b):
    if len(p) <= 1:
        return 0.
    cov = np.cov(np.vstack([p, b]), ddof=1)
    beta = cov[0][1] / cov[1][1]

    return beta


def cal_alpha(p_annua_profit, b_annua_profit, unrisk_rate, beta):

    return p_annua_profit - (unrisk_rate + beta * (b_annua_profit - unrisk_rate))


def cal_sharp(p_annua_profit, unrisk_rate, volatility):

    return (p_annua_profit - unrisk_rate) / volatility


def cal_downside_risk(p, b):
    mask = p < b
    diff = p[mask] - b[mask]
    if len(diff) <= 1:
        return 0.

    return (diff * diff).sum() / len(diff) ** 0.5 * YEAR_TRADE_DAYS ** 0.5


def cal_sortino(p_annua_profit, unrisk_rate, downside_risk):

    sortino = (p_annua_profit - unrisk_rate) / downside_risk
    return sortino


def align_series(p, b):
    if len(p) != len(b):
        while 1:
            diff = p["date"] - b["date"]
            diff_date = diff[diff != datetime.timedelta(days=0)]
            if len(diff_date) > 0:
                i = diff_date.index[0]
                if diff_date.iloc[0] > datetime.timedelta(days=0):
                    b.drop(b.index[i], inplace=True)
                    b.index = range(len(b))
                else:
                    p.drop(p.index[i], inplace=True)
                    p.index = range(len(p))
            else:
                break
    return p, b


class GetAlpha(CNTrade):
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq3.json')
        self.trade_time = get_date_now("CN")
        self.email = Email()

    def get_para_by_portfolio(self, p_name):
        self.xq.set_attr("portfolio_code", p_name)
        time.sleep(1)
        p, b = self.xq.get_profit_daily()
        if p and b:
            p, b = analyse_profit(p), analyse_profit(b)
            p, b = align_series(p, b)
            p_annua_profit = get_annualized_returns(p)
            b_annua_profit = get_annualized_returns(b)

            beta = cal_beta(p["daily"].values, b["daily"].values)
            alpha = cal_alpha(p_annua_profit, b_annua_profit, unrisk_rate, beta)
            volatility = cal_volatility(p["daily"].values)
            sharp = cal_sharp(p_annua_profit, unrisk_rate, volatility)
            maxdown = cal_max_drawdown(p["daily"].values)

            print portfolio_list[p_name]["name"] + ": alpha:" + str(alpha) + " beta:" + str(beta) + \
                  " sharp:" + str(sharp) + " volatility:" + str(volatility) + " maxdown:" + str(maxdown)

    def main(self, s, e, is_first):
        self.logger = get_logger(COLLECTION, name=str(s)+"-"+str(e), is_first=is_first)
        s = int(s)
        e = int(e)
        tmp = s

        try:
            for no in range(s, e):
                self.update_para()
                while is_trade_time(TEST_STATE, self.trade_time):
                    time.sleep(60 * 10)
                tmp = no
                p_name = unicode("ZH" + '{:0>6}'.format(no))
                self.xq.set_attr("portfolio_code", p_name)
                r = self.xq.get_profit_daily()
                if r:
                    p, b = r[0]["list"], r[1]["list"]
                    market = r[1]["symbol"][:2]
                    if len(p) > 0 and len(b) > 0:
                        start_date = p[0]["date"]
                        p, b = analyse_profit(p), analyse_profit(b)
                        p, b = align_series(p, b)
                        p_value, b_value = p["daily"].values, b["daily"].values
                        p_annua_profit   = get_annualized_returns(p)
                        b_annua_profit   = get_annualized_returns(b)

                        beta       = cal_beta(p_value, b_value)
                        alpha      = cal_alpha(p_annua_profit, b_annua_profit, unrisk_rate, beta)
                        volatility = cal_volatility(p_value)
                        sharp      = cal_sharp(p_annua_profit, unrisk_rate, volatility)
                        maxdown    = cal_max_drawdown(p["value"])
                        downside   = cal_downside_risk(p["daily"], b["daily"])
                        sortino    = cal_sortino(p_annua_profit, unrisk_rate, downside)
                        if alpha > 0 and sharp > 0:
                            self.xq.get_portfolio_html(p_name)
                            viewer = self.xq.get_viewer()
                            is_stop = self.xq.is_stop()
                            trade_times =self.xq.get_tradetimes()
                            state = "stop" if is_stop else "run"
                            name = self.xq.get_pname()
                            record_msg(self.logger, p_name + " " + name + ": a:" + str(get_four_five(alpha)) + " b:" + str(get_four_five(beta)) +\
                                       " sh:" + str(get_four_five(sharp)) + " d:" +str(get_four_five(maxdown)) + " so:" +\
                                       str(get_four_five(sortino)) + " t:" + str(trade_times) + " " + str(market) + " " + str(start_date) + " " + str(viewer) + " " + state )
        except Exception as e:
                msg = "get_alpha " + str(e) 
                record_msg(self.logger, msg=msg, email=self.email)
                traceback.print_exc()
                return tmp - 1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: python get_alpha.py startNo endNo"
        exit(-1)

    end = sys.argv[2]
    start = sys.argv[1]
    is_first = True

    while 1:
        if start:
            alpha = GetAlpha()
            start = alpha.main(start, end, is_first)
            # is_first = False
            time.sleep(60*10)
        else:
            break
