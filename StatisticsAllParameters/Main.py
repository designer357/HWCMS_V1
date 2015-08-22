# -*- coding:utf-8 -*-
__author__ = 'chengmin'
from bs4 import BeautifulSoup
import re
import os
import chardet
val2=[]
#inputhtml=open("Command_Reference_zh.hhc","rb").read()
#print(chardet.detect(inputhtml))

inputhtml=open("Command_Reference_zh.hhk","rb").readlines()
for eachline in inputhtml:
    soup=BeautifulSoup(eachline)
    pattern=re.compile(r'.*')
    val=soup.find_all(name='param',attrs={"name":"Name","value":pattern})
    if len(val)>0:
        pass
    else:
        continue
    for e in val:
        t0=str(e)
        t=str(e.param)
        t1=t0.replace(t,"")
        pattern2=re.compile(r"value=\".*\"")
        val2.append(pattern2.findall(str(t1))[0].split('=')[-1].replace("\"",''))
#for each in val2:
    #print(each)
val2=list(set(val2))
val3=val2
#val3=list(filter(lambda a:a.isalpha() or '-' in a or '(' in a or ')' in a or ' ' in a,val2))
for tab in range(len(val3)):
    val3[tab]=val3[tab].encode("utf-8")
    #format=chardet.detect(val3[tab])['encoding']
    #if chardet.detect(val3[tab])['encoding']=='ascii':
        #val3[tab]=val3[tab].decode("ascii").encode('gb2312')
    #else:
        #print chardet.detect(val3[tab])['encoding']
    #val3[tab]=val3[tab].decode(format).encode('utf-8')
with open(os.getcwd()+"/AllCommandersOutput.txt","a")as fout:
    for each in val3:
        fout.write(each.decode('utf-8'))
        fout.write('\n')
