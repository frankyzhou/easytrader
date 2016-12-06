from trade.util import *
import time

client = client(host="10.104.236.87")
all = ts.get_today_all()
codes = all["code"].values
for code in codes:
    order = "buy " + code + " 0.01 100"
    result = client.exec_order(order)
    if result != "OK":
        print order
    time.sleep(3)