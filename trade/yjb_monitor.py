from util import *
import sys
# c = client(host="10.104.236.87")
c = client(host="127.0.0.1")
while 1:
    try:
        print "Enter data to transmit: stop, get_position, buy, sell"
        data = sys.stdin.readline().strip()
        print c.exec_order(data)
    except Exception, e:
        print e
