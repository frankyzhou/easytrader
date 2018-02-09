# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import tushare as ts
import pandas as pd
import os

chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
options = webdriver.ChromeOptions()
# options.add_argument("user-data-dir=C:\Users\Administrator\AppData\Local\Google\Chrome\User Data")
options.add_argument("user-data-dir=C:\Users\\frankyzhou\AppData\Local\Google\Chrome\User Data")


class HKSpider:
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
        self.data = ts.get_today_all()
        self.trade_days = ts.get_k_data('sh', start='2017-03-17')['date'].values

    def get_holding(self, market):
        self.driver.get('http://sc.hkexnews.hk/TuniS/www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t='+market)
        for date in self.trade_days:
            if not os.path.exists(market + '/' + date + '.csv'):
                df = self.get_holding_by_oneday(date)
                df.to_csv(market + '/' + date + '.csv', encoding='gbk')
        pass

    def get_holding_by_oneday(self, date):
        day = date[-2:]
        month = date[5:7]
        year = date[:4]
        def_date = self.driver.find_element_by_id('pnlResult').text.split('\n')[0][-10:]
        if def_date[:2] != day:
            self.driver.find_element_by_id('ddlShareholdingDay').send_keys(day)
        if def_date[3:5] != month:
            self.driver.find_element_by_id('ddlShareholdingMonth').send_keys(month)
        if def_date[6:] != year:
            self.driver.find_element_by_id('ddlShareholdingYear').send_keys(year)
        self.driver.find_element_by_id('btnSearch').click()
        time.sleep(5)
        text = self.driver.find_element_by_id('pnlResult').text
        tks_all = text.split('\n')[4:]
        lst = []
        for tk in tks_all:
            tks = tk.split(' ')
            if tks[0][0] == '9':
                code = '60' + tks[0][1:]
            elif tks[0][:2] == '77':
                code = '300' + tks[0][2:]
            else:
                code = '00' + tks[0][1:]
            # code = pre + tks[0][1:]
            name = self.data[self.data.code == code]['name'].values[0]
            tmp = [code, name]
            tmp.extend(tks[-2:])
            lst.append(tmp)
        df = pd.DataFrame(lst)
        df.columns = ['code', 'name', 'volume', 'percent']
        return df

if __name__ == '__main__':
    hk = HKSpider()
    hk.get_holding('sz')
    hk.get_holding('sh')
    hk.driver.close()