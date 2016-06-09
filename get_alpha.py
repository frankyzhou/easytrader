__author__ = 'frankyzhou'
# -*- coding: utf-8 -*-
import easytrader
import pandas as pd
import datetime
import numpy as np

class get_alpha:
    def __init__(self):
        self.xq = easytrader.use('xq')
        self.xq.prepare('xq.json')
        self.xq.setattr("portfolio_code", "ZH776826")

    def get_annualized_returns(self, profit_list):
        total_profit = profit_list[-1:]["value"].values[0] -1
        annua_profit = total_profit / profit_list.index.size * 252
        return annua_profit

    def analyse_profit(self, profit_list):
        data = {'date':[],'daily':[],'value':[]}
        # df = pd.DataFrame(index=['date','percent','value'])
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
        r = np.cov(a, b)
        r = r[0][1]
        return r
    def get_volatility(self, p):
        pass

    def main(self):
        unrisk_rate = 0.025
        p, b = self.xq.get_profit_daily()
        p, b = self.analyse_profit(p), self.analyse_profit(b)
        p_annua_profit = self.get_annualized_returns(p)
        b_annua_profit = self.get_annualized_returns(b)
        cov = self.get_cov(p["daily"].values, b["daily"].values)
        beta = cov / np.std(b["daily"].values)
        alpha = p_annua_profit - (unrisk_rate + beta * (b_annua_profit - unrisk_rate))

if __name__ == '__main__':
    a = get_alpha()
    a.main()