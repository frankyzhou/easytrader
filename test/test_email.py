# -*- coding: utf-8 -*-
__author__ = 'frankyzhou'
'''
使用smtp和pop3 协议收发qq邮箱实验
用户名和密码需要自己填写
'''

# from smtplib import SMTP
# from smtplib import SMTPRecipientsRefused
import smtplib
from poplib import POP3
from time import sleep
import sys

smtpserver = 'smtp.163.com'
pop3server = 'pop.163.com'
emailaddr = 'zljszlj@163.com'
username = 'zljszlj@163.com'
password = 'zljabh37'

#组合邮件格式
origHeaders = ['From: zljszlj@163.com',
    'To: 847915049@qq.com',
    'Subject: test msg']
origBody = ['nihao ','yaan','sichuan']
origMsg = '\r\n\r\n'.join(['\r\n'.join(origHeaders),'\r\n'.join(origBody)])

#发送邮件部分
sendSer = smtplib.SMTP()
# sendSer.set_debuglevel(1)
# print sendSer.ehlo()[0] #服务器属性等
sendSer.connect(host=smtpserver, port=25)
sendSer.login(username,password) #qq邮箱需要验证
try:
   errs = sendSer.sendmail(emailaddr,emailaddr,origMsg)
   # sendSer.getreply()
except smtplib.SMTPRecipientsRefused:
   print 'server refused....'
   sys.exit(1)
sendSer.quit()
assert len(errs) == 0,errs


print '\n\n\nsend a mail ....OK!'
sleep(10) #等待10秒
print 'Now get the mail .....\n\n\n'



#开始接收邮件
revcSer = POP3(host=pop3server)
revcSer.user(username)
revcSer.pass_(password)

rsp,msg,siz = revcSer.retr(revcSer.stat()[0])
sep = msg.index('')
if msg:
   for i in msg:
      print i
revcBody = msg[sep+1:]
assert origBody == revcBody
print 'successful get ....'
