__author__ = 'frankyzhou'
import time
import socket
import socks
import httplib
import win_inet_pton
from stem import Signal
from stem.control import Controller

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket

def renew_tor():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password = 'zlj')
        controller.signal(Signal.NEWNYM)
        controller.close()

def showmyip():
    connectTor()
    print "connected to tor."
    # r = requests.get('http://icanhazip.com/')
    conn = httplib.HTTPConnection("icanhazip.com")
    conn.request("GET", "/")
    response = conn.getresponse()
    # ip_address = r.text.strip()
    print response.read()
    # print(ip_address)


for i in range(10):
    # renew_tor()
    # time.sleep(60)
#     connectTor()
    showmyip()
    renew_tor()
