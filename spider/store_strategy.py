# coding=utf8
import easytrader
import time
from bs4 import BeautifulSoup
from trade.util import *
import traceback
base_url = "https://xueqiu.com/v4/statuses/user_timeline.json?user_id=9796081404&page={0}&type=0&_=1479898855214"
COLLECTION = "xq_strategy"


class StoreStrategy:
    def __init__(self, p):
        self.xq = easytrader.use("xq")
        self.xq.prepare('../trade/config/xq'+p+'.json')
        self.db = MongoDB("strategy")
        self.logger = get_logger(COLLECTION)

    def deal_strategy(self, strategys):
        num = 0
        for s in strategys:
            msg_dict = {}
            html = s["description"]
            text = BeautifulSoup(html).text.split()
            if text[0][0] != "$":
                continue
            msg_dict["code"] = text[0]
            msg = text[1].split("#")
            # time = datetime.datetime.strptime(msg[0], "%m月%d日%H:%M入选")
            msg_dict["time"] = datetime.datetime.fromtimestamp(s["created_at"]/1000)
            msg_dict["title"] = msg[1]
            msg_dict["reason"] = msg[2][3:]
            if not self.db.get_doc(msg_dict["title"], msg_dict):
                self.db.insert_doc(msg_dict["title"], msg_dict)
                num += 1
            else:
                return True, num
        return False, num

    def main(self):
        maxPage = 20000
        i = 1
        result = False
        num = 0
        while i <= maxPage:
            maxPage, strategy = self.xq.get_strategy(i)
            time.sleep(10)
            try:
                result, num_tmp = self.deal_strategy(strategy)
                num += num_tmp
            except Exception:
                traceback.print_exc()
                time.sleep(60)
                continue
            i += 1
            record_msg(self.logger, str(i) + "/" + str(maxPage))
            if result:
                time.sleep(12 * 60 * 60)
                i = 1
                num = 0

if __name__  == "__main__":
    ss = StoreStrategy("3")
    ss.main()
