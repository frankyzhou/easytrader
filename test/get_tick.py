__author__ = 'frankyzhou'
import tushare as ts
import os
code = '000852'
date = '2016-08-09'
file = ".csv"
t = ts.get_tick_data(code=code, date= date)
filename = os.path.dirname(__file__) + "/" + code + file
t.to_csv(filename)