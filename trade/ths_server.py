# coding=utf-8
from util import *
from easytrader.pyautotrade_ths import *
import traceback
import easytrader

class ThsTrade:
    def __init__(self, is_first):
        self.server = get_server()
        self.logger = get_logger(COLLECTION, is_first=is_first)
        self.email = Email()

    def judge_opera(self, msg):
        msg = msg.split()
        type = msg[0]

        if type == STOP:
            return STOP

        if type == IPO:
            # if self._user.auto_ipo() == IPO:
            msg_dict = self._user.auto_ipo()
            record_msg(self.logger, msg=str(msg_dict['message']), subject="ipo", email=self.email)
            return 'ipo is done!'
            # else:
            #     return 'no ipo!'

        code = msg[1]

        if type == GET_POSITION:
            record_msg(self.logger, "查询仓位：" + code)
            return self.get_position_by_stock(code)

        price, amount = msg[2], msg[3]
        if type == BUY:
            record_msg(self.logger, "买入：" + code)
            return self._user.buy(code, price=price, amount=amount)
        elif type == SELL:
            record_msg(self.logger, "卖出：" + code)
            return self._user.sell(code, price=price, amount=amount)

        return "Nothing."

    def get_position_by_stock(self, code):
        position_broker = self._user.position
        position = {}
        balance = self._user.balance[0]
        total_money = float(balance['total_balance'])
        rest_money = float(balance['enable_balance'])
        enable = 0
        percent = 0.0
        for c in position_broker:
            code_tmp = c['证券代码']
            position[code_tmp] = {}
            position[code_tmp]["c_p"] = 100 * float(c["市值"]) / total_money
            position[code_tmp]["g_p"] = float(c["参考盈亏比例(%)"])
            position[code_tmp]["enable"] = float(c["可用余额"])
            position[code_tmp]["turnover"] = float(c["市值"])

        if code == "all":
            return position

        if code in position.keys():
            enable = position[code]["enable"]
            percent = position[code]["c_p"]
        return percent, enable, total_money, rest_money

    def main(self):
        self._ACCOUNT = os.environ.get('EZ_TEST_HT_ACCOUNT')
        self._PASSWORD = os.environ.get('EZ_TEST_HT_password')
        self._COMM_PASSWORD = os.environ.get('EZ_TEST_HT_comm_password')

        self._user = easytrader.use('gj_client')
        self._user.prepare(user=self._ACCOUNT, password=self._PASSWORD, comm_password=self._COMM_PASSWORD)

        address = 0
        while 1:
            try:
                request, address = self.server.recvfrom(READ_SIZE)
                response = self.judge_opera(request.decode('ascii'))
                self.server.sendto(str(response).encode('ascii'), address)
                if str(response) == STOP:
                    record_msg(self.logger, "人工停止")
                    return False
            except:
                traceback.print_exc()
                self.server.sendto(b'error', address)
                record_msg(self.logger, "重新启动")
                # self._user.exit()
                # return True

if __name__ == '__main__':
    result = True
    is_first = True
    while result:
        ths = ThsTrade(is_first)
        result = ths.main()
        is_first = False