# coding=utf-8
import sys
from cn_trade import *
import traceback
import tushare as ts
COLLECTION = "ths_monitor"
TEST_STATE = False


class ThsMonitor(CNTrade):
    def __init__(self, p, is_first):
        super(ThsMonitor, self).__init__(p=p)
        self.logger = get_logger(COLLECTION, is_first=is_first)
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
        print "\n"
        record_msg(self.logger, "sh:" + str(sh_amount) + ",  sz:" + str(sz_amount))

    def get_real_price(self):
        self.all_stocks_data = ts.get_today_all()
        for code in self.position:
            s = self.all_stocks_data[self.all_stocks_data.code == code]
            try:
                if s["changepercent"].values[0] > 7:
                    print "\n"
                    record_msg(self.logger, str(code) + " up to 7%!", email=self.email)
                if s["changepercent"].values[0] < -7:
                    print "\n"
                    record_msg(self.logger, str(code) + " down to 7%!", email=self.email)
            except:
                continue

    def sumup_today(self):
        now = datetime.datetime.now()
        if now > self.last_trade_time[3] + datetime.timedelta(hours=1) and not self.is_report:
            # 大于3点才开始执行
            self.position = str_to_dict(self.client.exec_order("get_position all"))
            self.get_real_price()
            self.is_report = True
            report = ""
            for code in self.position:
                df = ts.get_hist_data(code, start=self.last_trade_time[0].strftime("%Y-%m-%d"))
                if len(df) == 0:
                    continue  # 没有数据跳过
                close, ma5, ma10, ma20 = df["close"].values[0], df["ma5"].values[0], df["ma10"].values[0], df["ma20"].values[0]
                # v, v_ma5, v_ma10, v_ma20 = df["volume"].values[0], df["v_ma5"].values[0], df["v_ma10"].values[0], df["v_ma20"].values[0]
                p_change = df["p_change"].values[0]
                turnover = df["turnover"].values[0]
                c_percent = self.position[code]["c_p"]
                g_percent = self.position[code]["g_p"]
                name = get_code_name(self.all_stocks_data, code=code)
                code_mk = "H" if code[0] == "6" else "Z"
                url = "https://xueqiu.com/S/S" + code_mk + str(code)

                report += "*"*40 + "\n" + str(name) + " c:" + str(p_change) + " t:" +str(turnover) +\
                    " cp:" + str(round(c_percent,2)) + " gp:" + str(round(g_percent,2)) +\
                    "\np_ma: " + str(round(ma5/close,3)) + " " + str(round((ma10/close),3)) + " " + str(round(ma20/close,3)) +\
                           "\nURL:" + url + "\n"
            record_msg(self.logger, msg=report, subject="每日持仓报告", email=self.email)

    def ipo_am(self):
        now = datetime.datetime.now()
        if self.last_trade_time[1] < now < self.last_trade_time[2] and not self.is_ipo:
            self.client.exec_order("ipo", response=False) #不需要等待消息
            self.is_ipo = True

    def main(self):
        while 1:
            self.update_para(TEST_STATE)
            while is_trade_time(TEST_STATE, self.last_trade_time):
                try:
                    self.position = str_to_dict(self.client.exec_order("get_position all"))
                    self.get_real_price()
                    self.get_sh_sz_percent()
                    time.sleep(5 * 60)
                except Exception:
                    traceback.print_exc()
                    time.sleep(60)
            self.sumup_today()
            self.ipo_am()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: python ThsMonitor.py profilio_num[1,2,....n]"
        exit(-1)
    is_first = True
    while 1:
        xq = ThsMonitor(sys.argv[1], is_first)
        xq.main()
        time.sleep(60)
        is_first = False

