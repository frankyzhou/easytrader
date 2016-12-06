# coding=utf-8
from util import *
from easytrader.pyautotrade_ths import *
import traceback

COLLECTION = "yjb_operation"
GET_POSITION = "get_position"
BUY = "buy"
SELL = "sell"
STOP = "stop"
READ_SIZE = 8192


class ThsTrade:
    def __init__(self):
        self.server = get_server()
        self.logger = get_logger(COLLECTION)

    def judge_opera(self, msg):
        msg = msg.split()
        type = msg[0]

        if type == STOP:
            return STOP

        code = msg[1]

        if type == GET_POSITION:
            self.operation.clickRefreshButton()
            record_msg(self.logger, "查询仓位：" + code)
            return self.get_position_by_stock(code)

        price, amount = msg[2], msg[3]
        if type == BUY:
            record_msg(self.logger, "买入：" + code)
            return self.operation.order(code=code, price=price, direction="B", quantity=amount)
        elif type == SELL:
            record_msg(self.logger, "卖出：" + code)
            return self.operation.order(code=code, price=price, direction="S", quantity=amount)

        return "Nothing."

    def get_position_by_stock(self, code):
        position_broker = self.operation.getPosition()
        if code == "all":
            return position_broker
        rest_money = self.operation.getMoney()
        stock_money = 0.01
        if len(position_broker) > 0:
            for k in position_broker.keys():
                stock_money += position_broker[k]["turnover"]
        total_money = rest_money + stock_money
        enable = 0
        percent = 0.0
        if position_broker.has_key(code):
            enable = position_broker[code]["enable"]
            stock_turnover = position_broker[code]["turnover"]
            percent = stock_turnover / total_money
        return percent, enable, total_money

    def main(self):
        top_hwnd = findTopWindow(wantedText=u'网上股票交易系统5.0')
        if top_hwnd == 0:
            record_msg(self.logger, "无法找到客户端")
        else:
            self.operation = Operation(top_hwnd)
            record_msg(self.logger, "成功找到客户端")
        while 1:
            try:
                request, address = self.server.recvfrom(READ_SIZE)
                response = self.judge_opera(request)
                self.server.sendto(str(response), address)
                if str(response) == STOP:
                    record_msg(self.logger, "人工停止")
                    return False
            except:
                traceback.print_exc()
                record_msg(self.logger, "重新启动")
                return True

if __name__ == '__main__':
    result = True
    is_first = True
    while result:
        ths = ThsTrade()
        result = ths.main()