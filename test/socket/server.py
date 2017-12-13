# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'
import test.socket, traceback

host = '' # Bind to all interfaces
port = 51500

# Step1: 创建socket对象
s = test.socket.socket(test.socket.AF_INET, test.socket.SOCK_DGRAM)

# Step2: 设置socket选项(可选)
s.setsockopt(test.socket.SOL_SOCKET, test.socket.SO_REUSEADDR, 1)

# Step3: 绑定到某一个端口
s.bind((host, port))

# Step4: 监听该端口上的连接
while 1:
    try:
        message, address = s.recvfrom(1024)
        print "Got data from ", address

        s.sendto("Data is received succeefully.", address)
        a = 1/0
        print message

    # except (KeyboardInterrupt, SystemExit):
    #     print "raise"
    #     raise
    except Exception:
        print 1
        traceback.print_exc()