# -*- coding: utf-8 -*
import easytrader
from trade.util import *
import time, re, sys, datetime

__author__ = 'frankyzhou'
# declare basic vars
TEST_STATE = False
XUEQIU_DB_NAME = "Xueqiu"
COLLECTION = "history_operation"
SLIP_POINT = 0


class XqTrade:
    def __init__(self, p):
        # 固定部分
        self.xq = easytrader.use('xq')
        self.xq.prepare('config/xq'+p+'.json')
        self.xq.setattr("portfolio_code", "ZH776826")
        self.logger = get_logger(COLLECTION)
        self.db = MongoDB(XUEQIU_DB_NAME)
        self.email = Email()
        self.client = client(host="10.104.236.87")
        self.p_path = os.path.dirname(os.path.abspath(__file__)) + '/config/'+p+'.json'
        self.portfolio_list = helpers.file2dict(self.p_path)
        # 每日更新
        self.last_trade_time = get_trade_date_series("CN")
        self.trade_time = get_date_now("CN")
        self.is_update_stocks = False
        self.all_stocks_data = None

    def trade_by_entrust(self, entrust, k, factor, percent):
        """
        解析每个组合的交易记录
        :param entrust:
        :param k:
        :param factor:
        :param percent:
        :return:
        """
        for trade in entrust:
            # only if entrust is today or not finished by no trade time
            if not TEST_STATE:
                if not is_today(trade["report_time"], self.last_trade_time) or self.db.get_doc(COLLECTION, trade):
                    break
            else:
                if self.db.get_doc(COLLECTION, trade):
                    continue

            trade["portfolio"] = k
            record_msg(logger=self.logger, msg="-"*50 + "\n" + k + " updates new operation!" +
                                               " @ " + trade["report_time"])
            code = str(trade["stock_code"][2:])
            target_percent = trade["target_weight"] * percent /100 if trade["target_weight"] > 2.0 else 0.0
            """
            before_percent has two version.
            1.the position is caled by yjb;
            2,the position is caled by xq;
            已经有比例，故其他需要对应
            """
            before_percent_yjb, enable_amount, asset = parse_digit(self.client.exec_order("get_position "+ code))
            before_percent_xq = trade["prev_weight"] * percent / 100 if trade["prev_weight"] > 2.0 else 0.0
            dif, price, amount = self.get_trade_detail(target_percent, before_percent_xq,
                                                       before_percent_yjb, asset, factor, code, trade)

            result = self.trade(dif, code, price,amount, enable_amount)
            record_msg(logger=self.logger,
                       msg=self.portfolio_list[k]["name"] + ": " + result + " 花" + cal_time_cost(trade["report_time"]) + "s")
            self.db.insert_doc(COLLECTION, trade)

    def trade(self, dif, code, price, amount, enable_amount):
        """
         下单
        :param dif:
        :param code:
        :param price:
        :param amount:
        :param enable_amount:
        :return:
        """
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
                result = str_to_dict(self.client.exec_order("sell " + code + " " + str(price) + " " + str(amount)))
                result["trade"] = "卖出 "+code+" @ " + str(price) + " 共 " + str(amount)
            else:
                result["trade"] = "卖出不足100股 "+code+" @ " + str(price) + " 共 " + str(amount)
        elif dif == 0:
            result["trade"] = code + " 数量为0，不动！"

        result = result["error_info"] + result["trade"] if "error_info" in result else result["trade"]
        return result

    def get_trade_detail(self, target_percent, before_percent_xq, before_percent_yjb, asset, factor, code, trade):
        """
        得到交易变化，价格，数量
        :param target_percent:
        :param before_percent_xq:
        :param before_percent_yjb:
        :param asset:
        :param factor:
        :param code:
        :param trade:
        :return:
        """
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

    def update_para(self):
        """
        当每天自动运行到固定时间更新，否则启动时候更新
        :return:
        """
        now_time = datetime.datetime.now()
        update_begin_1 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 15, 0)
        update_begin_2 = datetime.datetime(int(now_time.year), int(now_time.month), int(now_time.day), 9, 15, 5)
        if update_begin_1 < now_time < update_begin_2:
            self.last_trade_time = get_trade_date_series("CN")
            self.trade_time = get_date_now("CN")
            self.is_update_stocks = False
            self.all_stocks_data = None

    def main(self):
        while 1:
            self.update_para()
            if is_trade_time(TEST_STATE, self.trade_time):
                self.is_update_stocks, self.all_stocks_data = update_stocks_data(self.is_update_stocks,
                                                                                 self.all_stocks_data)
                for k in self.portfolio_list.keys():
                    try:
                        self.xq.setattr("portfolio_code", k)
                        time.sleep(8)
                        entrust = self.xq.get_xq_entrust_checked()

                        factor = self.portfolio_list[k]["factor"]
                        percent = self.portfolio_list[k]["percent"]
                        self.trade_by_entrust(entrust, k, factor, percent)

                    except Exception, e:
                        msg = "xq:" + str(e.message)
                        record_msg(logger=self.logger, msg=msg, email=self.email)
                        return -1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python xq_trade.py profilio_num[1,2,....n]"
        exit(-1)
    while 1:
        xq = XqTrade(sys.argv[1])
        xq.main()
        time.sleep(60)
