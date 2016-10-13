# coding=utf-8
import time
from selenium import webdriver
import requests
from easytrader import helpers
from PIL import Image
# 该段代码在ubuntu上能成功运行，并没有在windows上面运行过
# 直接登陆新浪微博
def get_cha(cha_url):
    # cha_url ="http://login.sina.com.cn/cgi/pin.php?r=92566891&s=0&p=xd-96ef749270f86e5d62af7486888990aafcca"
    session = requests.session()
    cha_page = session.get(cha_url)
    with open("cha.jpg", 'wb') as f:
        f.write(cha_page.content)
        f.close()
    try:
        im = Image.open("cha.jpg")
        im.show()
        im.close()
    except:
        print(u"请到当前目录下，找到验证码后输入")


url = 'http://weibo.com/login.php'
driver = webdriver.Firefox()
driver.maximize_window()
driver.get(url)
time.sleep(10)
print('开始登陆')

# 定位到账号密码表单
login_tpye = driver.find_element_by_class_name('info_header').find_element_by_xpath('//a')
login_tpye.click()
time.sleep(10)

name_field = driver.find_element_by_id('loginname')
name_field.clear()
name_field.send_keys('752649673@qq.com')

password_field = driver.find_element_by_class_name('password').find_element_by_name('password')
password_field.clear()
password_field.send_keys('zljabhbhwan37')

submit = driver.find_element_by_link_text('登录')
submit.click()
time.sleep(15)

name_field = driver.find_element_by_id('loginname')
name_field.clear()
name_field.send_keys('752649673@qq.com')

password_field = driver.find_element_by_class_name('password').find_element_by_name('password')
password_field.clear()
password_field.send_keys('zljabhbhwan37')

submit = driver.find_element_by_link_text('登录')
submit.click()
time.sleep(15)
# 等待页面刷新，完成登陆
# vcode = driver.find_element_by_xpath("//*[@id=\"pl_login_form\"]/div/div[3]/div[3]")
# driver.find_element_by_xpath("//*[@id=\"pl_login_form\"]/div/div[3]/div[3]/div/input")
# driver.find_element_by_name("verifycode")
# vcode_pic_html = ""
# get_cha("")
driver.save_screenshot('aa.png')
imgelement = driver.find_element_by_xpath("//*[@id=\"pl_login_form\"]/div/div[3]/div[3]/a/img")  #定位验证码
location = imgelement.location  #获取验证码x,y轴坐标
size=imgelement.size
rangle=(int(location['x']),int(location['y']),int(location['x']+size['width']),int(location['y']+size['height']))
i=Image.open("aa.png") #打开截图
frame4=i.crop(rangle)  #使用Image的crop函数，从截图中再次截取我们需要的区域
frame4.save('frame4.jpg')
print('登陆完成')
sina_cookies = driver.get_cookies()

cookie = [item["name"] + "=" + item["value"] for item in sina_cookies]
cookiestr = '; '.join(item for item in cookie)

# 验证cookie是否有效
redirect_url = 'http://weibo.com/p/1005051921017243/info?mod=pedit_more'
headers = {'cookie': cookiestr}
html = requests.get(redirect_url, headers=headers).text
print(html)