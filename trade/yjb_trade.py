# -*- coding: utf-8 -*-

import easytrader
from trade.util import *

# declare basic vars
GET_POSITION = "get_position"
BUY = "buy"
SELL = "sell"
READ_SIZE = 8192


class yjb_trade:
    def __init__(self):
        self.yjb = easytrader.use('yjb')
        self.yjb.prepare('config/yjb.json')
        self.server = get_server()

    def judge_opera(self, msg):
        msg = msg.split()
        type, code = msg[0], msg[1]
        if type == GET_POSITION:
            return self.yjb.get_position()

        price, amount = msg[2], msg[3]
        if type == BUY:
            return self.yjb.buy(stock_code=code, price=price, amount=amount)
        elif type == SELL:
            return self.yjb.sell(stock_code=code, price=price, amount=amount)

        return "Nothing."

    def get_position_by_stock(self, code):

        position_yjb = self.yjb.get_position()
        balance = self.yjb.get_balance()[0]
        asset = balance["asset_balance"]
        return self.yjb.get_position_by_stock(code, position_yjb, asset), asset

    def main(self):
        while(1):
            #try:
                request, address = self.server.recvfrom(READ_SIZE)
                print "Got data from ", address

                response = self.judge_opera(request)
                self.server.sendto(str(response), address)

            #except Exception, e:
            #    print e

if __name__ == '__main__':
    yjb = yjb_trade()
    yjb.main()
    # str = [{u'stock_name': u'\u5b89\u742a\u9175\u6bcd',
    #         u'stock_code': u'600298', u'current_amount':
    #             200, u'enable_amount': 200, u'last_price':
    #             u'17.810', u'position_str': u'0003100000000003104000000010000000000A514313754600298',
    #         u'income_balance': 23.8, u'market_value': 3562.0, u'keep_cost_price': 17.691, u'cost_price'
    #         : 17.691}, {u'stock_name': u'\u4e07\u534e\u5316\u5b66', u'stock_code': u'600309', u'current_amount'
    # : 600, u'enable_amount': 600, u'last_price': u'20.850', u'position_str':
    #     u'0003100000000003104000000010000000000A514313754600309', u'income_balance': 615.26, u'market_value': 12510.0, u'keep_cost_price': 19.823, u'cost_price': 19.823}, {u'stock_name': u'\u9f99\u51c0\u73af\u4fdd', u'stock_code': u'600388', u'current_amount': 0, u'enable_amount': 0, u'last_price': u'14.140', u'position_str': u'0003100000000003104000000010000000000A514313754600388', u'income_balance': 516.32, u'market_value': 0.0, u'keep_cost_price': 13.5, u'cost_price': 13.5}, {u'stock_name': u'\u5ddd\u6295\u80fd\u6e90', u'stock_code': u'600674', u'current_amount': 2300, u'enable_amount': 2300, u'last_price': u'9.120', u'position_str': u'0003100000000003104000000010000000000A514313754600674', u'income_balance': -231.56, u'market_value': 20976.0, u'keep_cost_price': 9.221, u'cost_price': 9.221}, {u'stock_name': u'\u6cb1\u724c\u820d\u5f97', u'stock_code': u'600702', u'current_amount': 300, u'enable_amount': 300, u'last_price': u'22.670', u'position_str': u'0003100000000003104000000010000000000A514313754600702', u'income_balance': 12.42, u'market_value': 6801.0, u'keep_cost_price': 22.628, u'cost_price': 22.628}, {u'stock_name': u'\u592a\u5e73\u6d0b', u'stock_code': u'601099', u'current_amount': 1000, u'enable_amount': 1000, u'last_price': u'7.270', u'position_str': u'0003100000000003104000000010000000000A514313754601099', u'income_balance': 41.94, u'market_value': 7270.0, u'keep_cost_price': 7.228, u'cost_price': 7.228}, {u'stock_name': u'\u6cf8\u5dde\u8001\u7a96', u'stock_code': u'000568', u'current_amount': 200, u'enable_amount': 200, u'last_price': u'31.800', u'position_str': u'00031000000000031040000000200000000000159447604000568', u'income_balance': 93.04, u'market_value': 6360.0, u'keep_cost_price': 31.335, u'cost_price': 31.335}, {u'stock_name': u'\u534e\u8baf\u65b9\u821f', u'stock_code': u'000687', u'current_amount': 800, u'enable_amount': 800, u'last_price': u'21.100', u'position_str': u'00031000000000031040000000200000000000159447604000687', u'income_balance': 52.62, u'market_value': 16880.0, u'keep_cost_price': 21.034, u'cost_price': 21.034}, {u'stock_name': u'\u56fd\u5143\u8bc1\u5238', u'stock_code': u'000728', u'current_amount': 800, u'enable_amount': 800, u'last_price': u'20.560', u'position_str': u'00031000000000031040000000200000000000159447604000728', u'income_balance': 98.05, u'market_value': 16448.0, u'keep_cost_price': 20.437, u'cost_price': 20.437}, {u'stock_name': u'\u4e94 \u7cae \u6db2', u'stock_code': u'000858', u'current_amount': 100, u'enable_amount': 100, u'last_price': u'33.920', u'position_str': u'00031000000000031040000000200000000000159447604000858', u'income_balance': -28.89, u'market_value': 3392.0, u'keep_cost_price': 34.209, u'cost_price': 34.209}, {u'stock_name': u'\u7d22\u83f2\u4e9a', u'stock_code': u'002572', u'current_amount': 200, u'enable_amount': 200, u'last_price': u'56.980', u'position_str': u'00031000000000031040000000200000000000159447604002572', u'income_balance': -317.9, u'market_value': 11396.0, u'keep_cost_price': 58.571, u'cost_price': 58.571}, {u'stock_name': u'\u623f\u5730\u4ea7B', u'stock_code': u'150118', u'current_amount': 0, u'enable_amount': 0, u'last_price': u'0.518', u'position_str': u'00031000000000031040000000200000000000159447604150118', u'income_balance': 67.2, u'market_value': 0.0, u'keep_cost_price': 0.506, u'cost_price': 0.506}, {u'stock_name': u'\u5238\u5546B', u'stock_code': u'150201', u'current_amount': 0, u'enable_amount': 0, u'last_price': u'0.593', u'position_str': u'00031000000000031040000000200000000000159447604150201', u'income_balance': 389.5, u'market_value': 0.0, u'keep_cost_price': 0.57, u'cost_price': 0.57}, {u'stock_name': u'\u4e7e\u7167\u5149\u7535', u'stock_code': u'300102', u'current_amount': 1300, u'enable_amount': 0, u'last_price': u'9.950', u'position_str': u'00031000000000031040000000200000000000159447604300102', u'income_balance': 41.06, u'market_value': 12935.0, u'keep_cost_price': 9.918, u'cost_price': 9.918}, {u'stock_name': u'\u94f6\u79a7\u79d1\u6280', u'stock_code': u'300221', u'current_amount': 400, u'enable_amount': 400, u'last_price': u'26.600', u'position_str': u'00031000000000031040000000200000000000159447604300221', u'income_balance': 755.86, u'market_value': 10640.0, u'keep_cost_price': 24.708, u'cost_price': 24.708}]
    # list = byteify(str)
    # print list