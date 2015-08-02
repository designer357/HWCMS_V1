#!/usr/bin/env python
from InPutForRulesVersion2 import *
import collections
import numpy
mydict,mylist=returnAttributes()
ProjectPath="/Library/WebServer/Documents/HWCMS_V1"

#print(mydict)
A=[]
def Main(filelist):
    #A=[]
    for eachfile in filelist:
        with open(ProjectPath+'/ServerData1/'+eachfile)as fin:
            val=fin.readlines()
            print(val)
            A=list(filter(lambda a:islistcontainstr(mylist,a.strip().split(' ')[0].strip()),val))
            A=map(str.lstrip,A)
            print(A)
        C=collections.defaultdict(int)
        C_set=collections.defaultdict(int)
        D=collections.defaultdict(list)
        #print(A.count("            type internal;\n"))
        for eachattr in mylist:
            print(eachattr+" ........is ......")
            pattern=re.compile(r".*"+eachattr+".*\n")

            Temp_list=pattern.findall(''.join(A))
            print(Temp_list)
            C[eachattr]+=len(Temp_list)
            Temp_set=set(Temp_list)
            C_set[eachattr]+=len(Temp_set)
            T=[]
            for eachset in Temp_set:
                #print("--------"+eachset)
                T.append(Temp_list.count(eachset))
            D[eachattr] = T
        #print(''.join(A))
        print(C)
        print(C_set)
        #print(Temp_set)
        print(D)
        #for eachc in C_set:
        E=collections.defaultdict(int)
        for eachk,eachv in D.items():
            eachsum=sum(eachv)
            print(eachk)
            myarray=numpy.array(eachv)
            TTT1=myarray/float(eachsum)
            TTT2=numpy.log2(myarray/float(eachsum))
            #print(TTT1)
            #print(TTT2)
            #print(-numpy.dot(TTT1,TTT2))
            E[eachk]+=-numpy.dot(TTT1,TTT2)
        print(E)



for each in mylist:
    pass
filelist=["bgp_seat"]
Main(filelist)