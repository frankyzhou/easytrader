from trade.util import *
import time

client = client(host="10.104.236.87")
all = ts.get_today_all()
codes = all["code"].values
codes.sort()
black_list = ["300126"]
for i in range(0, len(codes), 1):
    code = codes[i]
    if code not in black_list:
        order = "buy " + code + " 0.01 100"
        result = client.exec_order(order)
        if result != "OK":
            print order, i
            break
        time.sleep(3)