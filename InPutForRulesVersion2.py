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
            #print("-------"+each+"--------"+str)
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



def returnAttributes(protocol,label_list):
    protocol=protocol.lower()
    filelist=os.listdir(ProjectPath)
    for eachfile in filelist:
        if '.xlsx' in eachfile:
            data=xlrd.open_workbook(os.path.join(ProjectPath,eachfile))
            table = data.sheets()[0]
            nrows = table.nrows #行数
            ncols = table.ncols #列数
            linescount=0
            mydict={}
            mylist=[]
            while linescount<nrows:

                if not len(str(table.col_values(1)[linescount]).lower())>0:
                    linescount+=1
                    continue
                if len(str(table.col_values(0)[linescount]).lower())>0 and str(table.col_values(0)[linescount]).lower() in protocol:
                    #print(str(table.col_values(0)[linescount]).lower())
                    flag=1
                else:
                    flag=0
                print("---------->")
                print(flag)
                if flag==0:
                    linescount += 1
                    continue
                elif flag==1:

                    tab1=0
                    linescount2=linescount
                    print(nrows-linescount2)
                    while tab1 < nrows-linescount2:
                        print("########"+str(table.col_values(0)[tab1]).lower()+str(linescount2))

                        if len(str(table.col_values(0)[tab1]).lower())==0:
                            #print(str(table.col_values(0)[linescount]).lower())
                            flag=1
                        elif len(str(table.col_values(0)[tab1]).lower())>0 and not str(table.col_values(0)[tab1]).lower() in protocol:
                            flag=0
                        print("++++++++++++++>")
                        print(flag)
                        if not (str(tab1+1) in label_list):
                            tab1 += 1
                            continue
                        else:
                            if len(str(table.row_values(linescount)[1]))>0:
                                mydict[str(table.row_values(tab1)[1])] = str(table.row_values(linescount2+tab1)[2])
                                mylist.append(str(table.row_values(linescount2+tab1)[1]))
                        tab1 += 1
                        linescount += 1
            return mydict,mylist
def MainFunc(filelist,filepath,protocol,linstr,outputfolder,label_list):
    mydict,mylist=returnAttributes(protocol,label_list)
    mylist3=mylist[:]
    for k,v in mydict.items():
        if '/' in v:
            vv=v.split('/')
            for e in vv:
                if len(e)>0:
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
        with open(filepath+'/'+eachfile)as fin:
            linsout=[]
            for eachline in fin:
                if "Authentication Data Removed" in eachline or '/*' in eachline:
                    #print(eachline)
                    pass
                else:
                    linsout.append(eachline)
        with open(filepath+'/'+eachfile,"w")as fout:
            fout.writelines(linsout)

        if len(eachfile)>0:
            print(eachfile)
            protocol2=r'[ \t]*'+protocol+'.*$'
            linstr2=r'[\s]*'+linstr+'[\s]*$'
            parse_file = CiscoConfParse(str(filepath+'/'+eachfile))

            #val_block0=parse_file.find_blocks(protocol2,exactmatch=False,ignore_ws=True)
            val_children0=parse_file.find_all_children(protocol2,exactmatch=False,ignore_ws=True)

            val0=val_children0
            #print("val_children000000")
            #print(val_children0)

            if str(linstr)!="input patterns":
                parse0 = CiscoConfParse(val0)
                val_block=parse0.find_blocks(linstr2,exactmatch=False,ignore_ws=True)
                #val_children=parse_file.find_children_w_parents(parentstr,linstr,ignore_ws=True)
                val_children=parse0.find_all_children(linstr2,exactmatch=False,ignore_ws=True)

                print("val_block...")
                print(val_block)
                print('val_children...')
                print(val_children)

                val1=val_block+val_children
            else:
                val1=val_children0
            #val1=val_children
            #print("val1///")
            #print(val1)
            parse1 = CiscoConfParse(val1)

            val2=[]
            for each in mylist:
                #print("each............................."+each)
                each2=r'[\s]*'+each+'[\w\s;\[\]\-\.]+.*'
                temp=parse1.find_all_children(each2,exactmatch=True,ignore_ws=True)
                val2.extend(temp)
            #val=parse.find_all_children('group CONNECTOR',exactmatch=False,ignore_ws=True)
            #print('val2....')
            #print(val2)
            val3=[]
            #print("mylist3........")
            #print(mylist3)
            for each in val2:
                itema=each.replace('{','').replace('#','').strip()+','
                if islistcontainstr(mylist3,each) and not itema in val3:
                    #print("+++++++++++++++++++++++++++++++++++++++++++++++++++++"+each)
                    val3.append(itema)

            Output=[]

            for tab in range(len(mylist)):
                Output.append([])

            for tab in range(len(mylist)):
                pattern=re.compile(r"[\s]*"+mylist[tab]+'.*')
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

#L=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15']
#L=['2','3']
#a,b=returnAttributes("isis",L)
#print(b)
#mylist=["atla","chic","clev","hous","kans","losa","newy32aoa","salt","seat","wash"]
#filelist=list(filter(lambda a: a in mylist,os.listdir(ProjectPath+'/ServerData2')))
#print(filelist)
#MainFunc(filelist,ProjectPath+'/ServerData2',"group CONNECTOR {","inputrules")

















