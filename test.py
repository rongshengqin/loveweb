# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as sp
import json

url='http://www.cool18.com/bbs4/'
html=requests.get(url)
soup=sp(html.text,"html.parser")
lis=soup.find_all('li',style=None)
ns=[]
for li in lis:
    text=li.text.split('bytes)')[0].split('(')
    s=int(text[-1])
    if s>1800:
        ur=url+li.a['href']
        ns.append([ur,text[0]])
        
url = 'http://overthewall-qrsyml.rhcloud.com/cron'
# 声明数据类型, 有些框架会自动识别并解析json
headers = {'Content-Type': 'application/json; charset=utf-8'}
form = {'cron': ns}
r = requests.post(url, data=json.dumps(form), headers=headers)
print r

