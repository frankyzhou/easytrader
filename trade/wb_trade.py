# -*- coding: utf-8 -*
import easytrader
import time, sys
from cn_trade import *
import traceback
# declare basic vars
TEST_STATE = False
DB_NAME = "Weibo"
COLLECTION = "history_operation"
SLIP_POINT = 0.02


class WBTrade(CNTrade):
    def __init__(self, p):
        super(WBTrade, self).__init__()
        # 固定部分
        self.wb = easytrader.use('wb')
        self.wb.prepare("config/wb.json")
        self.logger = get_logger(COLLECTION)
        self.db = MongoDB(DB_NAME)
        self.p_path = os.path.dirname(os.path.abspath(__file__)) + '/config/'+p+'.json'
        self.portfolio_list = helpers.file2dict(self.p_path)

    def trade_by_entrust(self, entrust, k, factor, percent, capital):
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
            code = str(trade["stock_code"])
            capital_tmp = capital / percent
            """
            before_percent has two version.
            1.the position is caled by yjb;
            2,the position is caled by xq;
            已经有比例，故其他需要对应
            """
            before_percent_yjb, enable_amount, asset = parse_digit(self.client.exec_order("get_position "+ code))
            dif, price, amount = self.get_trade_detail(asset, factor, code, trade, capital_tmp)

            result = self.trade(dif, code, price, amount, enable_amount)
            record_msg(logger=self.logger,
                       msg=self.portfolio_list[k]["name"] + ": " + result + " 花" + cal_time_cost(trade["report_time"]) + "s")
            self.db.insert_doc(COLLECTION, trade)

    def get_trade_detail(self, asset, factor, code, trade, capital):
        """
        得到交易变化，价格，数量
        :param asset:
        :param factor:
        :param code:
        :param trade:
        :return:
        """
        dif = trade["amount"] * trade["price"] / capital
        dif = dif if trade["trade_type"] == u"买入" else -dif
        factor = abs(factor) if dif > 0.0 else -abs(factor)
        price = get_price_by_factor(self.all_stocks_data, code, trade["price"], (1+factor))
        amount = abs(dif * asset) * (1+SLIP_POINT) // price // 100 * 100

        return dif, price, amount

    def update_port_capital(self, state, list):
        if not state:
            for key in list.keys():
                self.wb.set_attr("portfolio_code", key)
                list[key]["capital"] = self.wb.get_capital()
                time.sleep(5)
            state = True
        return state, list

    def main(self):
        while 1:
            self.update_para()
            if is_trade_time(TEST_STATE, self.trade_time):
                self.is_update_stocks, self.all_stocks_data = update_stocks_data(self.is_update_stocks,
                                                                                 self.all_stocks_data)
                self.is_update_ports, self.portfolio_list = self.update_port_capital(self.is_update_ports,
                                                                                self.portfolio_list)
                for k in self.portfolio_list.keys():
                    try:
                        self.wb.set_attr("portfolio_code", k)
                        time.sleep(5) # 5 + get_json 5 = 10

                        factor = self.portfolio_list[k]["factor"]
                        percent = self.portfolio_list[k]["percent"]
                        capital = self.portfolio_list[k]["capital"]

                        entrust = self.wb.get_entrust()
                        self.trade_by_entrust(entrust, k, factor, percent, capital)

                    except Exception, e:
                        traceback.print_exc()
                        msg = "xq:" + str(e.message)
                        record_msg(logger=self.logger, msg=msg, email=self.email)
                        return -1

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python wb_trade.py profilio_num[wb1,2,....n]"
        exit(-1)
    while 1:
        wb = WBTrade(sys.argv[1])
        wb.main()
        time.sleep(60)
