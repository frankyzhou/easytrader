# coding=utf-8
import sys
from cn_trade import *
import traceback
import tushare as ts
COLLECTION = "ths_monitor"
TEST_STATE = False


class ThsMonitor(CNTrade):
    def __init__(self, p):
        super(ThsMonitor, self).__init__(p=p)
        self.logger = get_logger(COLLECTION)
        self.position = {}
        self.email = Email()

    def get_sh_sz_percent(self):
        sh_amount = 0
        sz_amount = 0
        for code in self.position:
            if code[0] == "6":
                sh_amount += self.position[code]["turnover"]
            else:
                sz_amount += self.position[code]["turnover"]
        sh_amount = int(sh_amount/10000) * 1000
        sz_amount = int(sz_amount/5000) * 500
        record_msg(self.logger, "sh:" + str(sh_amount) + ",  sz:" + str(sz_amount))

    def get_real_price(self):
        df_all = ts.get_today_all()
        for code in self.position:
            s = df_all[df_all.code == code]
            if s["changepercent"] > 7:
                record_msg(self.logger, str(code) + " up to 7%!", email=self.email)
            if s["changepercent"] < -7:
                record_msg(self.logger, str(code) + " down to 7%!", email=self.email)

    def sumup_today(self):
        now = datetime.datetime.now()
        if now > self.trade_time[3] and not self.is_report:
            # 大于3点才开始执行
            today = now.strftime("%Y-%m-%d")
            self.is_report = True
            for code in self.position:
                df = ts.get_hist_data(code, start=today)
                close, ma5, ma10, ma20 = df["close"], df["ma5"], df["ma10"], df["ma20"]
                v, v_ma5, v_ma10, v_ma20 = df["volume"], df["v_ma5"], df["v_ma10"], df["v_ma20"]
                p_change = df["p_change"]
                turnover = df["turnover"]
                record_msg(self.logger, str(code) + " c:" + p_change + " t:" +str(turnover) +
                           "\np_ma: " + str(ma5/close) + " " + str(ma10/close) + " " + str(ma20/close) +
                           "\nv_ma: " + str(v_ma5/v) + " " + str(v_ma10/v) + " " + str(v_ma20/v)
                           , email=self.email)

    def main(self):
        while 1:
            self.update_para()
            while is_trade_time(TEST_STATE, self.trade_time):
                try:
                    self.position = str_to_dict(self.client.exec_order("get_position all"))
                    time.sleep(15 * 60)
                    self.get_real_price()
                    self.get_sh_sz_percent()
                except:
                    traceback.print_exc()
            self.sumup_today()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python ThsMonitor.py profilio_num[1,2,....n]"
        exit(-1)
    while 1:
        xq = ThsMonitor(sys.argv[1])
        xq.main()
        time.sleep(60)

