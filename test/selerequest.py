from seleniumrequests import Phantomjs

webdriver = Phantomjs()
response = webdriver.request('POST', 'url here', data={"param1": "value1"})
print response