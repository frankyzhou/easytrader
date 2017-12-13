# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'
import test.socket, sys, re


# Step1: 输入host和port信息
host = "127.0.0.1"
textport = 51500

# Step2: 创建socket对象
s = test.socket.socket(test.socket.AF_INET, test.socket.SOCK_DGRAM)
try:
    port = int(textport)
except ValueError:
    port = test.socket.getservbyname(textport, 'udp')

# Step3: 打开socket连接
s.connect((host, port))

# Step4: 发送数据
while 1:
    print "Enter data to transmit: "
    data = sys.stdin.readline().strip()
    s.sendall(data)

    # Step5: 接收服务器发过来的数据
    print "Looking for replies; press Ctrl-C or Ctrl-Break to stop"
    s.settimeout(10)
    buf = s.recv(2048)
    if not len(buf): break
    sys.stdout.write(buf)

    print "\n"