# coding=utf-8
import traceback
import sys
from util import *



while 1:
    try:
        c = client(host="127.0.0.1")
        print("Enter data to transmit: stop, get_position, buy, sell")
        data = sys.stdin.readline().strip()
        # time.sleep(5)
        # data = "get_position 0001"
        # data = "buy 000001 10.0 2000000"
        print(datetime.datetime.now().strftime("%H:%M:%S"))
        print(c.exec_order(data))
        print(datetime.datetime.now().strftime("%H:%M:%S"))

        # time.sleep(5)
        # data = "sell 300072 10.0 200000"
        # print data
        # print datetime.datetime.now().strftime("%H:%M:%S")x
        # c.exec_order(data)
        # print datetime.datetime.now().strftime("%H:%M:%S")
        #
        # time.sleep(5)
        # data = "sell 000001 10.0 200000"
        # print data
        # print datetime.datetime.now().strftime("%H:%M:%S")
        # c.exec_order(data)
        # print datetime.datetime.now().strftime("%H:%M:%S")
    except :
        traceback.print_exc()