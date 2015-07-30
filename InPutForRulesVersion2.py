#-*- coding: utf-8 -*-
__author__ = 'chengmin'
import xlrd
import re
import os
import shutil
from ciscoconfparse import CiscoConfParse
ProjectPath="/Library/WebServer/Documents/HWCMS_V1"

def iscontainingdigit(str):
    exclude="[\{\}]"
    pattern=re.compile(r"^(?![\{\}]).*[0-9]+(?![\{\}])")
    if pattern.match(str):
        return True
    else:
        return False
def islistcontainstr(list,str):
    for each in list:
        if str in each.strip() or each.strip() in str:
            return True
    return False
def islistcontainstr2(list,str):
    for each in list:
        if str==each.strip():
            return True
    return False
def myjoin(mystr,mylist):
    str=""
    for tab in range(len(mylist)-1):
        str=str+mystr+mylist[tab].strip()+''
    str=str+mystr+mylist[len(mylist)-1].strip()
    return str


def returnAttributes():
    filelist=os.listdir(ProjectPath)
    for eachfile in filelist:
        if '.xlsx' in eachfile:
            data=xlrd.open_workbook(os.path.join(ProjectPath,eachfile))
            table = data.sheets()[0]
            nrows = table.nrows #行数
            ncols = table.ncols #列数
            mydict={}
            mylist=[]

            for tab1 in range(nrows):
                    mydict[str(table.row_values(tab1)[1])] = str(table.row_values(tab1)[2])
                    mylist.append(str(table.row_values(tab1)[1]))

            return mydict,mylist

def MainFunc(filelist,filepath,linstr,outputfolder):
    mydict,mylist=returnAttributes()
    mylist3=mylist[:]
    for k,v in mydict.items():
        if '/' in v:
            vv=v.split('/')
            for e in vv:
                mylist3.append(e)

    #filelist=os.listdir(filepath)
    for eachfile in filelist:
        if '.DS' in eachfile:
            continue
        with open(ProjectPath+"/"+outputfolder+"/input_"+linstr,"w")as fout:
            pass

    for eachfile in filelist:
        if '.DS' in eachfile:
            continue
        if len(eachfile)>0:
            print(eachfile)
            linstr2=r'[\s]*'+linstr+'[\s]*$'
            parse_file = CiscoConfParse(str(filepath+'/'+eachfile))
            val_block=parse_file.find_blocks(linstr2,exactmatch=True,ignore_ws=True)
            #val_children=parse_file.find_children_w_parents(parentstr,linstr,ignore_ws=True)
            val_children=parse_file.find_all_children(linstr2,exactmatch=True,ignore_ws=True)

            #print(val_block)
            #print(val_children)
            val1=val_block+val_children
            parse1 = CiscoConfParse(val1)

            val2=[]
            for each in mylist:
                temp=parse1.find_all_children(each,exactmatch=False,ignore_ws=True)
                val2.extend(temp)
            #val=parse.find_all_children('group CONNECTOR',exactmatch=False,ignore_ws=True)

            val3=[]
            for each in val2:
                if islistcontainstr(mylist3,each):
                    val3.append(each.replace('{','').replace('#','').strip()+',')

            Output=[]

            for tab in range(len(mylist)):
                Output.append([])

            for tab in range(len(mylist)):
                pattern=re.compile(r"^"+mylist[tab]+'.*')
                for each in val3:
                    matchlist=pattern.findall(each)
                    if matchlist:
                        Output[tab].extend(matchlist)
            #print(Output)
            #print(filepath+"/output"+linstr)
            with open(ProjectPath+"/"+outputfolder+"/input_"+linstr,"a")as fout:
                for each in Output:
                    fout.writelines(each)
                fout.write('\n')
            #print("success")
            #print(val3)

mylist=["atla","chic","clev","hous","kans","losa","newy32aoa","salt","seat","wash"]
filelist=list(filter(lambda a: a in mylist,os.listdir(ProjectPath+'/ServerData2')))
print(filelist)
MainFunc(filelist,ProjectPath+'/ServerData2',"group CONNECTOR {","inputrules")

















