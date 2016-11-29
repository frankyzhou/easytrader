# coding=utf-8
import sys
from cn_trade import *
COLLECTION = "ths_monitor"
TEST_STATE = True


class ThsMonitor(CNTrade):
    def __init__(self, p):
        super(ThsMonitor, self).__init__(p=p)
        self.logger = get_logger(COLLECTION)
        self.position = {}

    def get_sh_sz_percent(self):
        sh_amount = 0
        sz_amount = 0
        for code in self.position:
            if code[0] == "6":
                sh_amount += self.position[code]["turnover"]
            else:
                sz_amount += self.position[code]["turnover"]
        return sh_amount, sz_amount

    def main(self):
        while 1:
            self.update_para()
            while is_trade_time(TEST_STATE, self.trade_time):
                self.position = str_to_dict(self.client.exec_order("get_position all"))
                sh_amount, sz_amount = self.get_sh_sz_percent()
                record_msg(self.logger, "sh:" + str(sh_amount) + ",  sz:" + str(sz_amount))
                time.sleep(15 * 60)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python ThsMonitor.py profilio_num[1,2,....n]"
        exit(-1)
    while 1:
        xq = ThsMonitor(sys.argv[1])
        xq.main()
        time.sleep(60)

