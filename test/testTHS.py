from trade.util import *
import time

client = client(host="10.104.236.87")
all = ts.get_today_all()
codes = all["code"].values
black_list = ["300126"] 
for code in codes:
    if code not in black_list:
        order = "buy " + code + " 0.01 100"
        result = client.exec_order(order)
        if result != "OK":
            print order, result
            break
        time.sleep(3)