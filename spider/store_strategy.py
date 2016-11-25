# coding=utf8
import easytrader
import time
from bs4 import BeautifulSoup
from easytrader.MongoDB import *

base_url = "https://xueqiu.com/v4/statuses/user_timeline.json?user_id=9796081404&page={0}&type=0&_=1479898855214"


class StoreStrategy:
    def __init__(self, p):
        self.xq = easytrader.use("xq")
        self.xq.prepare('../trade/config/xq'+p+'.json')
        self.db = MongoDB("strategy")

    def deal_strategy(self, strategys):
        for s in strategys:
            msg_dict = {}
            html = s["description"]
            text = BeautifulSoup(html).text.split()
            msg_dict["code"] = text[0]
            msg = text[1].split("#")
            # time = datetime.datetime.strptime(msg[0], "%m月%d日%H:%M入选")
            msg_dict["time"] = datetime.datetime.fromtimestamp(s["created_at"]/1000)
            msg_dict["title"] = msg[1]
            msg_dict["reason"] = msg[2][3:]
            if not self.db.get_doc(msg_dict["title"], msg_dict):
                self.db.insert_doc(msg_dict["title"], msg_dict)

    def main(self):
        maxPage = 10
        i = 1
        while i <= maxPage:
            maxPage, strategy = self.xq.get_strategy(i)
            time.sleep(10)
            i += 1
            self.deal_strategy(strategy)

if __name__  == "__main__":
    ss = StoreStrategy("3")
    ss.main()
