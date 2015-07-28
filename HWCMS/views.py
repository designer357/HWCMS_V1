# -*- coding=utf-8 -*-
from django.shortcuts import render
from django.template import Template, Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponse,HttpResponseRedirect
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
import os,time,re
from stat import *
import InPutForRulesVersion2
from Apriori import *
from HWCMS.models import Parameter,FileList


global excludelist
global gloffset
global mylist
global datagridpagesize
global TotalFileList,TotalFileNameList
global FilesStoreFolder

ProjectPath="/Library/WebServer/Documents/HWCMS_V1"
excludelist=[]
mylist=[]
gloffset=-1
datagridpagesize=5
FilesStoreFolder="ServerData1"
TotalFileList=[]
TotalFileNameList=[]
for eachfile in os.listdir(os.path.join(ProjectPath,FilesStoreFolder)):
    if '.' in eachfile:
        suffix=eachfile.split('.')[1]
    else:
        suffix=""
    Time=os.stat(os.path.join(ProjectPath,FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
    timeTuple = time.localtime(Time)
    timestr=time.strftime('%Y-%m-%d',timeTuple)
    check=""
    TotalFileList.append(FileList(eachfile,timestr,suffix,check))
    TotalFileNameList.append(eachfile)

class Rule:
    def __init__(self,rule):
        self.rule=rule
def current_datetime(request):
    # 计算当前日期和时间，并以 datetime.datetime 对象的形式保存为局部变量 now
    now = datetime.datetime.now()

    #构建Html响应，使用now替换占位符%s
    html = "<html><body>It is now %s.</body></html>" % now

    #返回一个包含所生成响应的HttpResponse对象
    return HttpResponse(html)
# Create your views here.
def hours_ahead(request, offset):
    offset = int(offset)
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)

    return HttpResponse(html)

def JumpToIndex(request,n):
    return HttpResponseRedirect('/HWCMS/index/')

def isalliteminlistinstr(mylist,mystr):
    val=''.join(mylist).split(',')
    for tab in range(len(val)):
        val[tab]=val[tab].strip()
    for each in val:
        #print("-----------")
        #print(mystr)
        if each.strip() in mystr:
            pass
        else:
            return False,each.strip()
    return True,''

def replacerightbyerror(mylist,mystr):
    val=''.join(mylist).split(',')
    for tab in range(len(val)):
        val[tab]=val[tab].strip()
    str_list=mystr.split(',')
    for tab in range(len(str_list)):
        str_list[tab]=str_list[tab].strip()
    for each in str_list:
        if each.strip() in val:
            pass
        else:
            right=isalliteminlistinstr(mylist,mystr)[1]

            v1,v2=each.strip().split(':',1)
            v3,v4=isalliteminlistinstr(mylist,mystr)[1].split(':',1)
            if v1.strip()!=v3.strip():
                continue

            #print("222222222222222:"+mylist)
            myindex=str_list.index(each.strip())
            if myindex>=0:
                #print("----------"+str(myindex))
                str2=mystr.replace(each.strip(),right,1)
            #str2=','.join(str_list)
            #print("The Left of this Error is: "+str(str2.count(each.strip())))
            #print("+++++++"+str(each)+'++++++'+str(myindex))
            return str2,each.strip()
    return str,''

def file_upload(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList

    tempfullfilelist=[]
    tempfilenamelist=[]

    if not os.path.isdir(os.path.join(ProjectPath,FilesStoreFolder)):
        os.makedirs(os.path.join(ProjectPath,FilesStoreFolder))

    #if request.POST["MyFileList"]:
        #print(request.POST.getlist("MyFileList"))

    files = request.FILES.getlist('multifile')
    for f in files:
        tempfilenamelist.append(f.name)
        tempfullfilelist.append(os.path.join(ProjectPath,FilesStoreFolder)+'/' + f.name)


    for f in files:
        if f.name in TotalFileNameList:
            f.name = f.name.split('.')[0] + '_copy.' + f.name.split('.')[1]
        destination = open(os.path.join(ProjectPath,FilesStoreFolder)+'/' + f.name,'wb+')

        for chunk in f.chunks():
            destination.write(chunk)


    for eachfile in tempfilenamelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.path.join(ProjectPath,FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check=""
        if not eachfile in TotalFileNameList:
            TotalFileList.append(FileList(eachfile,timestr,suffix,check))
            TotalFileNameList.append(eachfile)
        else:
            eachfile = eachfile.split('.')[0] + '_copy.' + eachfile.split('.')[1]
            TotalFileList.append(FileList(eachfile,timestr,suffix,check))
            TotalFileNameList.append(eachfile)
    result=file_show(request,1)
    return result
def LoadRules(group):
    with open(os.getcwd()+"/results/RulesFor_"+group)as fin:
        Rules=[[],[]]
        pattern1=re.compile(r'set\(.*\)')
        lines=fin.readlines()
        for eachline in lines:
            print(eachline)
            #print(list(filter(lambda a: a!='{',pattern.findall(eachline))))
            list1=pattern1.findall(eachline)
            #print(len(list1))
            list_cond=[]
            list_result=[]
            list_cond2=[]
            list_result2=[]
            if len(list1)>0:
                list_cond,list_result=list1[0].split('-->')

            #print(list_cond)
            pattern2=re.compile(r"\'.*\'")
            if len(list_cond)>1:
                list_cond2=pattern2.findall(list_cond)
                for tab in range(len(list_cond2)):
                    list_cond2[tab]=list_cond2[tab].replace('\'','')
                #print(list_cond2)

            #print(list_result)
            if len(list_result)>1:
                list_result2=pattern2.findall(list_result)
                for tab in range(len(list_result2)):
                    list_result2[tab]=list_result2[tab].replace('\'','')
                #print(list_result2[0])
            if len(list_cond2)>0:
                Rules[0].append(list_cond2)
            if len(list_result2)>0:
                Rules[1].append(list_result2)
            if len(list_result2)>1:
                print("AAAAAAAAA")

    return Rules
def file_upload_for_detection(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList
    global mylist
    global patterns
    global lengthofmylist,pages,nextpage,previouspage,pagelist,ruleslist,TopList,interests



    files = request.FILES.getlist('multifile')

    group=patterns
    rules=LoadRules(group)
    detectedrulelist=[]

    #print("The number of total rules is "+str(len(rules[0]))+'\n')
    #print(rules)
    #with open("Detected Log.txt","w")as fout:
        #pass
    tempfilenames=[]
    for f in files:
        tempfilenames.append(f.name)
        destination = open(os.path.join(ProjectPath,"detect_temp")+'/' + f.name,'wb+')
        for chunk in f.chunks():
            destination.write(chunk)

        InPutForRulesVersion2.MainFunc(tempfilenames,ProjectPath+'/detect_temp',group,"detect_temp_inputrules")
        with open(ProjectPath+"/detect_temp_inputrules/"+"input_"+group)as fin:
            for eachline in fin.readlines():
                if len(eachline)>1:
                    val=''.join(eachline)
                flag3=-1
                count=0
                tab=0
                while tab <(len(rules[0]))-1:
                    tab=tab+1
                    flag1=-1
                    flag2=-1
                    try:
                        if isalliteminlistinstr(rules[0][tab],val)[0]:
                            flag1=1
                            error_detail1=isalliteminlistinstr(rules[0][tab],val)[1]
                        else:
                            error_detail1=isalliteminlistinstr(rules[0][tab],val)[1]
                            flag1=0
                        if isalliteminlistinstr(rules[1][tab],val)[0]:
                            flag2=1
                            error_detail2=isalliteminlistinstr(rules[1][tab],val)[1]
                        else:
                            error_detail2=isalliteminlistinstr(rules[1][tab],val)[1]
                            flag2=0
                    except:
                        pass
                    if flag1==1 and flag2==0:
                        count += 1

                        #print(")
                        #print("The Left of this Error is: "+str(val.count(detected))+'\n')
                        with open(os.getcwd()+"/Log/Detected Log.txt","a")as fout:
                            fout.write("Violate the "+str(tab+1)+"th Rule.  The Right form should be :"+str(error_detail1)+"    "+str(error_detail2)+'\n')
                            print("ere33333##############################")
                            print(rules[0][tab][0]+','+rules[1][tab][0])
                            print(val)
                            #val,detected=replacerightbyerror(rules[0][tab][0]+','+rules[1][tab][0],val)
                            detectedrule="----------"+str(f.name)+"-------Violate the "+str(tab+1)+"th Rule.  The Right form should be :"+\
                                    str(error_detail1)+"    "+str(error_detail2)+'\n'
                                    #"The Error is : "+str(detected)+'\n'+"The Left of this Error is: "+str(val.count(detected))+"----------------\n"
                            detectedrulelist.append(detectedrule)
                            #print(rules[0][tab][0]+"-->"+rules[1][tab][0]+'\n')
                            #fout.write("The Error is :  "+str(detected)+'\n')
                            #fout.write("The Left of this Error is: "+str(val.count(detected))+'\n')
                            fout.write(detectedrule)
                            flag3=1
                            #tab -= 1
                            fout.write('--------------------------------------------------------------------------------------------------------------------------------\n')
                    #else:
                        #flag3=-1

                print("--------------------------"+str(count)+" rules detected.")
            if flag3==-1:
                TotalFileList.append(os.getcwd()+'/'+FilesStoreFolder+'/'+f.name)
                TotalFileNameList.append(f.name)
                Nondetectedrule="+++++++++++++++++++++++"+str(f.name)+"+++++++++++++++++++++No Violations."
                detectedrulelist.append(Nondetectedrule)
        print("-----------------------------------------------------------------------"+str(patterns))
    if os.path.isfile(ProjectPath+"/templates/T3.html"):
        fp = open(ProjectPath+"/templates/T3.html")
        t = Template(fp.read())
        fp.close()
    else:
        print("Template Does Not Exist!!!")
    html = t.render(Context({'DetectedRuleList':detectedrulelist,'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'list':TotalFileList,'TheTopList':TopList,'DataGridPageSize':datagridpagesize,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    return HttpResponse(html)



    #return rule_show(request)
@csrf_exempt
def rule_show(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList
    global mylist
    global patterns
    global lengthofmylist,pages,nextpage,previouspage,pagelist,ruleslist,TopList,interests

    if os.path.isfile(ProjectPath+"/templates/T2.html"):
        fp = open(ProjectPath+"/templates/T2.html")
        t = Template(fp.read())
        fp.close()
    else:
        print("Template Does Not Exist!!!")
    html = t.render(Context({'RulesList':ruleslist,'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'list':TotalFileList,'TheTopList':TopList,'DataGridPageSize':datagridpagesize,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    return HttpResponse(html)



def rule_generate(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList
    global mylist
    global patterns
    global lengthofmylist,pages,nextpage,previouspage,pagelist,ruleslist,TopList,interests

    lengthofmylist=len(TotalFileList)

    pages=int(lengthofmylist / datagridpagesize) + (lengthofmylist % datagridpagesize > 0)

    nextpage=pages
    previouspage=0
    pagelist=[]
    ruleslist=[]
    TopList=[]
    interests=[]
    templist=[]

    try:
        for tab in range(datagridpagesize):
            TopList.append(TotalFileList[tab+(gloffset-1)*datagridpagesize])
    except:
        pass
    for tab in range(pages):
        pagelist.append(str(tab+1))



    para=Parameter(float(request.POST.get("paraMinSupp")),float(request.POST.get("paraMinCond"))\
                   ,float(request.POST.get("paraMinLift")),float(request.POST.get("paraMinKulc")),float(request.POST.get("paraThreshIR")))
    patterns=str(request.POST.get("strPattern"))
    interests.append(patterns)
    rulesfolder="inputrules"

    #starttime = time.time()
    #timestart = time.clock()

    if not os.path.isdir(ProjectPath+'/'+rulesfolder):
        os.makedirs(ProjectPath+'/'+rulesfolder)
    if not os.path.isdir(str(ProjectPath+'/results')):
        os.makedirs(str(ProjectPath+'/results'))

    for each in interests:
        #InputForRules.GenerateInputForRules(eachgroup)
        with open(ProjectPath+'/'+rulesfolder+"/input_"+each,"w")as fout:
            pass
        with open(ProjectPath+"/results/RulesFor_"+each,"w")as fout:
            pass
    for each in TotalFileList:
        templist.append(each.filename)
    for each in interests:
        print(each+" is processing......")
        InPutForRulesVersion2.MainFunc(templist,os.path.join(ProjectPath,FilesStoreFolder),each.strip(),rulesfolder)
        a = Apriori(para.min_supp,ProjectPath+'/'+rulesfolder+"/input_"+each)
        ls = a.do()
        rules = a.ralationRules(ls.get(ls.size()).items,para.min_cond,para.min_lift,para.min_kulc,para.thresh_ir)
        rule_count=0
        for rule in rules:
            rule_count += 1
            ruleslist.append(str(rule_count)+'th'+str(rule))
        with open(ProjectPath+"/results/RulesFor_"+each,"a")as fout:
            fout.write("min_support is "+str(para.min_supp)+".  min_confidence is "+str(para.min_cond)+"\n")
            for rule in rules:
                fout.write(str(rule)+'\n')
            fout.write("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    #endtime =  time.time()
    #time_elapsed = time.clock() - timestart
    #time_2=endtime-starttime
    #print("It takes %f milliseconds to find the above  patterns" %(time_2 * 1000))
    #print('耗时：', time_elapsed, 's')
    #temptime=str(self.label_timecost.text())+' '+str(time_elapsed)+' '+'s'
    #tempmemory=str(self.label_memorycost.text())+' '+str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)+' '+'bytes'
    #self.label_timecost.setText(QtCore.QString(temptime))
    #self.label_memorycost.setText(QtCore.QString(tempmemory))



    for tab in range(len(request.POST.getlist("FileName"))):
        if 'fsf' in request.POST.getlist("FileName")[tab]:
            #print(request.POST.getlist("FileName")[tab])
            excludelist.append(TopList[tab].filename)
    #print("EXCLUDE!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #print(gloffset)
    #print(list(set(excludelist)))

    return rule_show(request)
def my_cmp(v1,v2):
    p = re.compile("(\d+)")
    d1 = [int(i) for i in p.findall(v1)][0]
    d2 = [int(i) for i in p.findall(v2)][0]
    return cmp(d1, d2)
def my_cmp_filelist(v1,v2):
    p = re.compile("(\d+)")
    d1 = [int(i) for i in p.findall(v1.filename)][0]
    d2 = [int(i) for i in p.findall(v2.filename)][0]
    return cmp(d1, d2)
def my_cmp_py3(v1):
    p = re.compile("(\d+)")
    d1 = [int(i) for i in p.findall(v1)][0]
    #d2 = [int(i) for i in p.findall(v2)][0]
    return d1

def file_show(request,offset):
    global TotalFileList
    global TotalFileNameList
    myoffset=int(offset)

    global gloffset
    gloffset=int(offset)

    currentpage=myoffset

    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    filtername=str(request.POST.get("FilterName"))
    filterdate=str(request.POST.get("FilterDate"))
    filtertype=str(request.POST.get("FilterType"))
    TotalFileNameList2=[]
    TotalFileList2=[]
    for eachitem in TotalFileList:
        #print(eachitem.filename+" is ..................processing"+"***************"+str(len(eachitem.filetype)))
        try:
            if filtername=="Filename" or filtername=="None":
                pass
            else:
                if filtername in eachitem.filename:
                    pass
                else:
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)

            if filterdate=="Y/Y-M/Y-M-D" or filterdate=="None":
                pass
            else:
                if filterdate in eachitem.filedate:
                    pass
                else:
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)

            if filtertype==".suffix" or filtertype=="None":
                pass
            elif filtertype=="":
                if len(str(eachitem.filetype))==0:
                    pass
                else:
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)
            else:
                if len(eachitem.filetype)>0 and eachitem.filetype in filtertype:
                    pass
                else:
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)
        except:
            pass

    TotalFileList=list(set(TotalFileList).difference(set(TotalFileList2)))
    TotalFileNameList=list(set(TotalFileNameList).difference(set(TotalFileNameList2)))


    try:
        TotalFileNameList.sort(my_cmp)
        TotalFileList.sort(my_cmp_filelist)
    except:
        pass


    lengthofmylist=len(TotalFileList)
    #datagridpagesize=5
    TopList=[]
    pagelist=[]
    pages=int(lengthofmylist / datagridpagesize) + (lengthofmylist % datagridpagesize > 0)
    try:
        for tab in range(datagridpagesize):
            TopList.append(TotalFileList[tab+(myoffset-1)*datagridpagesize])
    except:
        pass
    if myoffset<pages:
        nextpage=myoffset+1
    else:
        nextpage=pages
    if myoffset>0:
        previouspage=myoffset-1
    else:
        previouspage=0
    for tab in range(pages):
        pagelist.append(str(tab+1))
    if os.path.isfile(ProjectPath+"/templates/T1.html"):
        fp = open(ProjectPath+"/templates/T1.html")
        t = Template(fp.read())
        fp.close()
    else:
        print("Template Does Not Exist!")
    print(TopList)
    html = t.render(Context({'CurrentPage':currentpage,'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,\
                             'list':TotalFileList,'TheTopList':TopList,'DataGridPageSize':datagridpagesize,\
                             'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    #return render_to_response('T1.html',locals())
    return HttpResponse(html)
def index_page(request):
    global TotalFileList
    global TotalFileNameList
    TotalFileList=[]
    TotalFileNameList=[]
    for eachfile in os.listdir(os.path.join(ProjectPath,FilesStoreFolder)):
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.path.join(ProjectPath,FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check=""
        TotalFileList.append(FileList(eachfile,timestr,suffix,check))
        TotalFileNameList.append(eachfile)
    global excludelist
    excludelist=[]

    checklist=[]
    TopList=[]
    previouspage=1
    #datagridpagesize=5
    lengthofmylist=len(TotalFileList)
    nextpage=5
    pages=int(lengthofmylist / datagridpagesize) + (lengthofmylist % datagridpagesize > 0)
    pagelist=[]

    for tab in range(datagridpagesize):
        checklist.append("")
    for tab in range(pages):
        pagelist.append(str(tab+1))
    if os.path.isfile(ProjectPath+"/templates/T1.html"):
        fp = open(ProjectPath+"/templates/T1.html")
        t = Template(fp.read())
        fp.close()
    else:
        print("Template Does Not Exist!!!")
    html = t.render(Context({'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,\
                             'list':TotalFileList,'TheTopList':TopList,'DataGridPageSize':datagridpagesize,\
                             'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    return HttpResponse(html)

    #return render_to_response('T1.html',locals())
def send_message(request):
    name = "Joe Lennon"
    sent_date = datetime.datetime.now()
    #return render_to_response(ProjectPath+'/templates/U1.html', locals())
    return render_to_response('U1.html', locals())

def file_delete(request,offset):
    print(request.POST)
    i_str=request.POST.get("FileNameToDelete")
    print(i_str)
    print(TotalFileNameList)
    index=TotalFileNameList.index(i_str)
    print(len(TotalFileNameList))
    print(len(TotalFileList))
    TotalFileNameList.pop(index)
    TotalFileList.pop(index)
    print("Delete@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@7")
    print(len(TotalFileList))
    print(len(TotalFileNameList))
    return file_show(request,offset)

