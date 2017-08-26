# coding=utf8
import time
from selenium import webdriver
import pandas as pd


chromedriver = "C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\Users\\frankyzhou\AppData\Local\Google\Chrome\User Data")
driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
driver.get("http://202.96.245.182/xxcx/ddyy.jsp?lm=5")
time.sleep(1)

info_dict = {'hospital':[], 'level':[]}

for t in range(146):
    e_list = driver.find_element_by_id('m_content').text.split('\n')
    index = 0
    for i in range(len(e_list)):
        e = e_list[i]
        if len(e) > 0 and e[0] == u'所':
            index = i
            break

    for j in range(index+1, len(e_list)-1):
        e = e_list[j]
        context = e.split()
        author = context[1]
        comment = context[3] if len(context) ==4 else u'no'
        if author not in info_dict['hospital']:
            tmp1 = info_dict['hospital']
            tmp2 = info_dict['level']
            tmp1.append(author)
            tmp2.append(comment)
            info_dict['hospital'] = tmp1
            info_dict['level'] = tmp2

    more = driver.find_elements_by_xpath("//*[@href]")[-1]
    more.click()
    time.sleep(1)
df = pd.DataFrame(info_dict)
df.to_excel('hospital.xlsx')
driver.quit()