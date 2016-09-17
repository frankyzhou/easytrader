__author__ = 'frankyzhou'
import time
import socket
import socks
import requests
from stem import Signal
from stem.control import Controller
import win_inet_pton
import easytrader
import json

controller = Controller.from_port(port=9051)
def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket
def renew_tor():
    controller.authenticate(password = 'zlj')
    controller.signal(Signal.NEWNYM)
def showmyip():
    r = requests.get('http://icanhazip.com/')
    ip_address = r.text.strip()
    print(ip_address)
# xq = easytrader.use('xq')
# xq.prepare('../trade/config/xq2.json')
def get(code):
    data = {
            "cube_symbol": code
        }
    url = "https://xueqiu.com/cubes/nav_daily/all.json"
    r = requests.get(url, params=data)
    # r = json.loads(r.text)
    return r.text

for i in range(10):
    renew_tor()
    connectTor()
    showmyip()
    # list = xq.get_profit_daily()
    print get("ZH743053")
    time.sleep(10)