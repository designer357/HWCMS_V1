# -*- coding=utf-8 -*-
from django.shortcuts import render
from django.template import Template, Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponse
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

excludelist=[]
mylist=[]
gloffset=-1
datagridpagesize=5
FilesStoreFolder="ServerData1"
TotalFileList=[]
TotalFileNameList=[]
for eachfile in os.listdir(os.path.join(os.getcwd(),FilesStoreFolder)):
    if '.' in eachfile:
        suffix=eachfile.split('.')[1]
    else:
        suffix=""
    Time=os.stat(os.path.join(os.getcwd(),FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
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

def file_upload(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList

    tempfullfilelist=[]
    tempfilenamelist=[]

    if not os.path.isdir(os.path.join(os.getcwd(),FilesStoreFolder)):
        os.makedirs(os.path.join(os.getcwd(),FilesStoreFolder))


    if request.POST["MyFileList"]:
        print(request.POST.getlist("MyFileList"))

    print("11111111111111111111111111111111111111")
    files = request.FILES.getlist('multifile')
    #print(files)
    for f in files:
        #print(f.name)
        #destination = open(os.path.join(os.getcwd(),FilesStoreFolder)+'/' + f.name,'wb+')
        #for chunk in f.chunks():
            #pass
            #print(chunk)
        #destination.close()
        tempfilenamelist.append(f.name)
        tempfullfilelist.append(os.path.join(os.getcwd(),FilesStoreFolder)+'/' + f.name)
    print("222222222222222222222222222222222222222")


    for eachfile in tempfilenamelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.path.join(os.getcwd(),FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
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
    for f in files:
        if f.name in TotalFileNameList:
            f.name = f.name.split('.')[0] + '_copy.' + f.name.split('.')[1]
        destination = open(os.path.join(os.getcwd(),FilesStoreFolder)+'/' + f.name,'wb+')

        for chunk in f.chunks():
            destination.write(chunk)







    result=file_show(request,1)
    return result

@csrf_exempt
def rule_generate(request):
    global datagridpagesize
    global TotalFileList,TotalFileNameList
    print(request.POST)
    global mylist
    lengthofmylist=len(TotalFileList)
    #datagridpagesize=5
    checklist=[]

    pages=int(lengthofmylist / datagridpagesize) + (lengthofmylist % datagridpagesize > 0)

    nextpage=pages
    previouspage=0
    pagelist=[]
    ruleslist=[]
    TopList=[]
    interests=[]
    templist=[]

    for tab in range(datagridpagesize):
        checklist.append("")
    try:
        for tab in range(datagridpagesize):
            TopList.append(TotalFileList[tab+(gloffset-1)*datagridpagesize])
    except:
        pass
    for tab in range(pages):
        pagelist.append(str(tab+1))
    if os.path.isfile(os.getcwd()+"/templates/T2.html"):
        fp = open(os.getcwd()+"/templates/T2.html")
        t = Template(fp.read())
        fp.close()
    else:
        print("Template Does Not Exist!!!")


    para=Parameter(float(request.POST.get("paraMinSupp")),float(request.POST.get("paraMinCond"))\
                   ,float(request.POST.get("paraMinLift")),float(request.POST.get("paraMinKulc")),float(request.POST.get("paraThreshIR")))

    patterns=str(request.POST.get("strPattern"))
    interests.append(patterns)
    rulesfolder="inputrules"

    #starttime = time.time()
    #timestart = time.clock()

    if not os.path.isdir(os.getcwd()+'/'+rulesfolder):
        os.makedirs(os.getcwd()+'/'+rulesfolder)
    if not os.path.isdir(str(os.getcwd()+'/results')):
        os.makedirs(str(os.getcwd()+'/results'))

    for each in interests:
        #InputForRules.GenerateInputForRules(eachgroup)
        with open(os.getcwd()+'/'+rulesfolder+"/input_"+each,"w")as fout:
            pass
        with open(os.getcwd()+"/results/RulesFor_"+each,"w")as fout:
            pass
    for each in TotalFileList:
        templist.append(each.filename)
    for each in interests:
        print(each+" is processing......")
        InPutForRulesVersion2.MainFunc(templist,os.path.join(os.getcwd(),FilesStoreFolder),each.strip(),rulesfolder)
        a = Apriori(para.min_supp,os.getcwd()+'/'+rulesfolder+"/input_"+each)
        ls = a.do()
        rules = a.ralationRules(ls.get(ls.size()).items,para.min_cond,para.min_lift,para.min_kulc,para.thresh_ir)
        rule_count=0
        for rule in rules:
            rule_count += 1
            ruleslist.append(str(rule_count)+'th'+str(rule))
        with open(os.getcwd()+"/results/RulesFor_"+each,"a")as fout:
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


    html = t.render(Context({'RulesList':ruleslist,'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'list':TotalFileList,'TheTopList':TopList,'DataGridPageSize':datagridpagesize,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    for tab in range(len(request.POST.getlist("FileName"))):
        if 'fsf' in request.POST.getlist("FileName")[tab]:
            #print(request.POST.getlist("FileName")[tab])
            excludelist.append(TopList[tab].filename)
    #print("EXCLUDE!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #print(gloffset)
    #print(list(set(excludelist)))

    return HttpResponse(html)
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
        print(eachitem.filename+"is ..................processing")
        try:
            if filtername=="Filename" or filtername=="None":
                #print("HAHA1")
                pass
            else:
                if filtername in eachitem.filename:
                    pass
                else:
                    print("to be ... 1..."+eachitem.filename)
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)
            if filterdate=="Y/Y-M/Y-M-D" or filterdate=="None":
                pass
            else:
                if filterdate in eachitem.filedate:
                    pass
                else:
                    print("to be ... 2..."+eachitem.filename)
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)

            if filtertype==".suffix" or filtertype=="None":
                pass
            else:
                if len(eachitem.filetype)>0 and eachitem.filetype in filtertype:
                    print("HAHA666666666"+eachitem.filename+"dsfsdffd"+eachitem.filetype)
                    pass
                else:
                    print("to be ...33333333333333333333333333..."+eachitem.filename+filtertype+eachitem.filetype)
                    print(eachitem.filename)
                    for each in TotalFileNameList:
                        print(each+'\n')
                    print("--------------------------------111"+str(len(TotalFileNameList)))
                    TotalFileNameList2.append(eachitem.filename)
                    TotalFileList2.append(eachitem)
                    print("--------------------------------222"+str(len(TotalFileNameList)))
                    for each in TotalFileNameList:
                        print(each+'\n')
        except:
            print(eachitem.filename)

    TotalFileList=list(set(TotalFileList).difference(set(TotalFileList2)))
    TotalFileNameList=list(set(TotalFileNameList).difference(set(TotalFileNameList2)))

    print(TotalFileList)

    try:
        TotalFileNameList.sort(my_cmp)
        TotalFileList.sort(my_cmp_filelist)
    except:
        pass

    print(TotalFileNameList)

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
    if os.path.isfile(os.getcwd()+"/templates/T1.html"):
        fp = open(os.getcwd()+"/templates/T1.html")
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
    for eachfile in os.listdir(os.path.join(os.getcwd(),FilesStoreFolder)):
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.path.join(os.getcwd(),FilesStoreFolder)+'/'+eachfile)[ST_MTIME]
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
    if os.path.isfile(os.getcwd()+"/templates/T1.html"):
        fp = open(os.getcwd()+"/templates/T1.html")
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
    #return render_to_response(os.getcwd()+'/templates/U1.html', locals())
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

