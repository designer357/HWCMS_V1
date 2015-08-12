#!/usr/bin/env python
from InPutForRulesVersion2 import *
import collections
import numpy
ProjectPath="/Library/WebServer/Documents/HWCMS_V1"



def Main(filelist,filepath,protocol,label_list):
    mydict,mylist=returnAttributes(protocol,label_list)
    TotalIdf=collections.defaultdict(int)
    Result=collections.defaultdict(int)
    FILECOUNT=0
    B=[]
    print("fafasdfafafafafdsf"+protocol)
    print(label_list)

    for eachfile in filelist:
        FILECOUNT += 1
        with open(filepath+'/'+eachfile)as fin:
            val=fin.readlines()
            #print(val)
            A=list(filter(lambda a:islistcontainstr(mylist,a.strip().split(' ')[0].strip()),val))
            A=map(str.lstrip,A)
            B.extend(A)
            #print(A)
            TotalSet_OneDocument=[]
            for eachattr in mylist:
                pattern=re.compile(r".*"+eachattr+".*\n")

                Temp_list=pattern.findall(''.join(A))
                Temp_set=set(Temp_list)
                TotalSet_OneDocument.extend(list(Temp_set))


            for eachone in TotalSet_OneDocument:
                TotalIdf[eachone]+=1


    #Compute the Entropy-----------------------------
    C=collections.defaultdict(int)
    #C_set=collections.defaultdict(int)
    D1=collections.defaultdict(dict)
    D2=collections.defaultdict(list)
    #print(A.count("            type internal;\n"))
    for eachattr in mylist:
        #print(eachattr+" ........is ......")
        pattern=re.compile(r".*"+eachattr+".*\n")

        Temp_list=pattern.findall(''.join(B))
        #print(Temp_list)
        C[eachattr]+=len(Temp_list)
        Temp_set=set(Temp_list)
        T1=collections.defaultdict(int)
        T2=[]
        TotalSet_OneDocument.extend(list(Temp_set))
        #C_set[eachattr]+=len(Temp_set)
        for eachset in Temp_set:
            #print("--------"+eachset)
            T1[eachset]=Temp_list.count(eachset)
            T2.append(Temp_list.count(eachset))
        D1[eachattr]=dict(T1)

        D2[eachattr]=T2

    E=collections.defaultdict(int)
    for eachk,eachv in D2.items():
        eachsum=sum(eachv)
        #print(eachk)
        myarray=numpy.array(eachv)
        TTT1=myarray/float(eachsum)
        TTT2=numpy.log2(myarray/float(eachsum))
        E[eachk]+=-numpy.dot(TTT1,TTT2)



    #print(E)
    print(TotalIdf)
    #print(D1)
    #print(A)

    for each,value in TotalIdf.items():
        #print(each)
        k=each.split(' ')[0]
        Result[each] = numpy.log2(float(FILECOUNT)/TotalIdf[each])*E[k]
        #Result[each] = (float(FILECOUNT))
        #Result[each]=E[k]


    return Result,TotalIdf,E,D1,D2 # D1 is the Term Frequence



#filelist=["atla","chic","seat"]
#Result,TotalIdf,E,D1,D2=Main(filelist,ProjectPath+"/ServerData2")
#print(T)
#print(T)
#print(T)

#print(Main(filelist)["peer-as 1001;\n"])
