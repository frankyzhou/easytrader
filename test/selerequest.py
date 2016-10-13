from seleniumrequests import PhantomJS

webdriver = PhantomJS()
response = webdriver.request('GET', 'http://m.weibo.cn/container/getIndex?containerid=231048zh200217')
print response