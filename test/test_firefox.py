from seleniumrequests import Firefox

from selenium import webdriver


browser = webdriver.PhantomJS()

browser.get("http://www.baidu.com")
browser.find_element_by_id("kw").send_keys("51job")
browser.find_element_by_id("su").click()
browser.quit()