# coding=utf-8
import sys
from cn_trade import *
COLLECTION = "ths_monitor"
TEST_STATE = False


class ThsMonitor(CNTrade):
    def __init__(self, p):
        super(ThsMonitor, self).__init__(p=p)
        self.logger = get_logger(COLLECTION)

    def main(self):
        while 1:
            self.update_para()
            while is_trade_time(TEST_STATE, self.trade_time):
                self.client.exec_order("get_position 600100", response=False)
                record_msg(self.logger, "reflash....")
                time.sleep(15 * 60)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python ThsMonitor.py profilio_num[1,2,....n]"
        exit(-1)
    while 1:
        xq = ThsMonitor(sys.argv[1])
        xq.main()
        time.sleep(60)

