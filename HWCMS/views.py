# coding=utf-8
from django.shortcuts import render
from django.template import Template, Context,RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import HttpResponse
import datetime
#import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
import os,time,re
from stat import *
import InPutForRulesVersion2
from Apriori import *

global excludelist
excludelist=[]
global gloffset
global mylist
mylist=[]
gloffset=-1
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
class FileList:
    def __init__(self,filename,filedate,filetype,check):
        self.filename=filename
        self.filedate=filedate
        self.filetype=filetype
        self.check=check
def file_info4(request):
    global mylist
    mylist=[]

    tempfullfilelist=[]
    tempfilenamelist=[]

    if not os.path.isdir(os.getcwd()+'/ServerData1'):
        os.makedirs(os.getcwd()+'/ServerData1')


    print("The FILE_INFO4 is CALLED")

    if request.POST["MyFileList"]:
        print(request.POST.getlist("MyFileList"))

    print("11111111111111111111111111111111111111")
    files = request.FILES.getlist('multifile')
    print(files)
    for f in files:
        print(f.name)
        #mylist.append(f.name)
        destination = open(os.getcwd()+'/ServerData1/' + f.name,'wb+')
        for chunk in f.chunks():
            #pass
            #print(chunk)
            destination.write(chunk)
        #destination.close()
        tempfilenamelist.append(f.name)
        tempfullfilelist.append(os.getcwd()+'/ServerData1/' + f.name)
    print("222222222222222222222222222222222222222")


    for eachfile in tempfilenamelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.getcwd()+'/ServerData1/'+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check="checked"
        mylist.append(FileList(eachfile,timestr,suffix,check))





    result=file_info2(request,1)
    return result
class Parameter:
    def __init__(self,supp,cond,lift,kulc,ir):
        self.min_supp=supp
        self.min_cond=cond
        self.min_lift=lift
        self.min_kulc=kulc
        self.thresh_ir=ir
@csrf_exempt
def file_info3(request):
    global mylist
    """
    filelist=os.listdir(os.getcwd()+'/data')
    filelist=sorted(filelist,my_cmp)
    for eachfile in filelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.getcwd()+'/data'+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check="checked"
        mylist.append(FileList(eachfile,timestr,suffix,check))
    """
    if request.method == 'POST':
        print("WWWWWWWWWWWWWWWWWWWWWWWWWWW")
        print(request.body)
    #if request.POST["paraMinSupp"]:
        #print("hahahahahaPPPPPPPPPPPPPPPPPPPPPPPP")
        #print(request.POST.get("paraMinSupp"))
        #req = json.loads(request.body)
    if not request.POST.has_key("strName"):
        pass
      #return ""
    if request.POST["FileName"]:
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
        print(','.join(request.POST.getlist("FileName")))
        #print(','.join(request.POST.getlist("FileName")))

      #return ','.join(request.POST.getlist("strName"))
    else:
        pass
      #return ""

    checklist=[]
    for tab in range(5):
        checklist.append("checked")
    #for tab in range(5):
        #if 'fsf' in request.POST.getlist("FileName")[tab]:
            #checklist[tab]=""


    basePath="http://127.0.0.1:8000/fileinfo/"
    lengthofmylist=len(mylist)
    Thetoplength=5

    TopList=[]
    #pages=int(round(lengthofmylist*1.0/Thetoplength))
    pages=int(lengthofmylist / Thetoplength) + (lengthofmylist % Thetoplength > 0)

    try:
        for tab in range(Thetoplength):
            TopList.append(mylist[tab+(gloffset-1)*Thetoplength])
    except:
        pass

    nextpage=pages

    previouspage=0



    pagelist=[]
    for tab in range(pages):
        pagelist.append(str(tab+1))

    ruleslist=[]
    #ruleslist.append("Rule1\n")
    #ruleslist.append("Rule2\n")
    #ruleslist.append(Rule("Rule1"))
    #ruleslist.append(Rule("Rule2"))
    # Simple way of using templates from the filesystem.
    # This is BAD because it doesn't account for missing files!
    #fp = open('/Users/chengmin/PycharmProjects/DjangoProject2ForHuaWei/templates/T2.html')
    fp = open(os.getcwd()+"/templates/T2.html")
    t = Template(fp.read())
    fp.close()
    #html = t.render(Context({'current_date': now}))


    para=Parameter(float(request.POST.get("paraMinSupp")),float(request.POST.get("paraMinCond"))\
                   ,float(request.POST.get("paraMinLift")),float(request.POST.get("paraMinKulc")),float(request.POST.get("paraThreshIR")))



    patterns=str(request.POST.get("strPattern"))
    #interests=["ipv4-family vpnv4"]
    interests=[]
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
    templist=[]
    for each in mylist:
        templist.append(each.filename)

    for each in interests:
        print(each+" is processing......")
        InPutForRulesVersion2.MainFunc(templist,os.getcwd()+'/ServerData1',each.strip(),rulesfolder)
        #print(para.min_supp)
        #print(os.getcwd()+'/'+rulesfolder+"/input_"+each)
        #print("daafasfds")
        a = Apriori(para.min_supp,os.getcwd()+'/'+rulesfolder+"/input_"+each)
        ls = a.do()
        rules = a.ralationRules(ls.get(ls.size()).items,para.min_cond,para.min_lift,para.min_kulc,para.thresh_ir)
        rule_count=0
        for rule in rules:
            #print(rule)
            rule_count += 1
            ruleslist.append(str(rule_count)+'th'+str(rule))
            #L=QListWidgetItem(self.listWidget)
            #L.setText(QtCore.QString(str(rule_count)+'th'+str(rule)))
        with open(os.getcwd()+"/results/RulesFor_"+each,"a")as fout:
            fout.write("min_support is "+str(para.min_supp)+".  min_confidence is "+str(para.min_cond)+"\n")
            for rule in rules:
                fout.write(str(rule)+'\n')
            fout.write("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
    #endtime =  time.time()
    #time_elapsed = time.clock() - timestart
    #time_2=endtime-starttime
    #print("It takes %f milliseconds to find the above  patterns" %(time_2 * 1000))
    #print()
    #print('耗时：', time_elapsed, 's')
    #temptime=str(self.label_timecost.text())+' '+str(time_elapsed)+' '+'s'
    #tempmemory=str(self.label_memorycost.text())+' '+str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)+' '+'bytes'
    #self.label_timecost.setText(QtCore.QString(temptime))
    #self.label_memorycost.setText(QtCore.QString(tempmemory))


































    html = t.render(Context({'RulesList':ruleslist,'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'basePath':basePath,'list':mylist,'TheTopList':TopList,'TheTopLength':Thetoplength,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    for tab in range(len(request.POST.getlist("FileName"))):
        if 'fsf' in request.POST.getlist("FileName")[tab]:
            print(request.POST.getlist("FileName")[tab])
            excludelist.append(TopList[tab].filename)
    print("EXCLUDE!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(gloffset)
    print(list(set(excludelist)))

    return HttpResponse(html)
def my_cmp(v1,v2):
    p = re.compile("(\d+)")
    d1 = [int(i) for i in p.findall(v1)][0]
    d2 = [int(i) for i in p.findall(v2)][0]
    return cmp(d1, d2)

def file_info2(request,offset):
    global mylist
    myoffset=int(offset)
    print("FileInfo22222222222222222222222222222222222222222")
    print(mylist)
    """
    filelist=os.listdir(os.getcwd()+'/data')
    mylist=[]
    filelist=sorted(filelist,my_cmp)
    for eachfile in filelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.getcwd()+'/data'+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check="checked"
        mylist.append(FileList(eachfile,timestr,suffix,check))
    """
    global gloffset
    gloffset=int(offset)

    if request.method == 'GET':
        print("WWWWWWWWWWWWWWWWWWWWWWWWWWW")
        print(request.body)
        #req = json.loads(request.body)

    if not request.POST.has_key("strName"):
        pass
      #return ""
    try:
        if request.POST["strName"]:
            print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQ")
            print(','.join(request.POST.getlist("strName")))
            #print(','.join(request.POST.getlist("FileName")))

            #return ','.join(request.POST.getlist("strName"))
        else:
            pass
    except:
        pass
      #return ""

    basePath="http://127.0.0.1:8000/fileinfo/"
    lengthofmylist=len(mylist)
    Thetoplength=5

    TopList=[]
    #pages=int(round(lengthofmylist*1.0/Thetoplength))
    pages=int(lengthofmylist / Thetoplength) + (lengthofmylist % Thetoplength > 0)


    try:
        for tab in range(Thetoplength):
            TopList.append(mylist[tab+(myoffset-1)*Thetoplength])
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



    pagelist=[]
    for tab in range(pages):
        pagelist.append(str(tab+1))

    # Simple way of using templates from the filesystem.
    # This is BAD because it doesn't account for missing files!
    #fp = open('/Users/chengmin/PycharmProjects/DjangoProject2ForHuaWei/templates/T1.html')
    fp = open(os.getcwd()+"/templates/T1.html")
    t = Template(fp.read())
    fp.close()
    #html = t.render(Context({'current_date': now}))
    html = t.render(Context({'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'basePath':basePath,'list':mylist,'TheTopList':TopList,'TheTopLength':Thetoplength,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    #fav_color = request.session['FileName']
    print("FFFFFFFFFFFFFFFFFFFFFFFRRRRRRRRRRRRRRRRRRRRRRR")
    #print(fav_color)
    return HttpResponse(html)
def file_info(request):
    global excludelist
    excludelist=[]
    """
    filelist=os.listdir(os.getcwd()+'/data')
    filelist=sorted(filelist,my_cmp)
    for eachfile in filelist:
        if '.' in eachfile:
            suffix=eachfile.split('.')[1]
        else:
            suffix=""
        Time=os.stat(os.getcwd()+'/data'+'/'+eachfile)[ST_MTIME]
        timeTuple = time.localtime(Time)
        timestr=time.strftime('%Y-%m-%d',timeTuple)
        check="checked"
        mylist.append(FileList(eachfile,timestr,suffix,check))
    """
    #if request.method == 'POST':
        #req = json.loads(request.body)
    #if not request.POST.has_key("strName"):
        #pass


    checklist=[]
    for tab in range(5):
        checklist.append("checked")

    basePath="http://127.0.0.1:8000/fileinfo/"

    TopList=[]

    nextpage=3

    previouspage=1

    Thetoplength=3

    lengthofmylist=len(mylist)

    #pages=lengthofmylist/Thetoplength
    pages=int(lengthofmylist / Thetoplength) + (lengthofmylist % Thetoplength > 0)

    pagelist=[]
    for tab in range(pages):
        pagelist.append(str(tab+1))

    # Simple way of using templates from the filesystem.
    # This is BAD because it doesn't account for missing files!
    #fp = open('/Users/chengmin/PycharmProjects/DjangoProject2ForHuaWei/templates/T1.html')
    fp = open(os.getcwd()+"/templates/T1.html")
    t = Template(fp.read())
    fp.close()
    #html = t.render(Context({'current_date': now}))
    html = t.render(Context({'Pages':pages,'NextPage':nextpage,'PreviousPage':previouspage,'basePath':basePath,'list':mylist,'TheTopList':TopList,'TheTopLength':Thetoplength,'lengthofmylist':lengthofmylist,"PagesList":pagelist}))

    return HttpResponse(html)
    #t = get_template('T1.html')
    #html = t.render(Context(locals()))
    #return HttpResponse(html)
    #return render_to_response('T1.html',locals())
#from datagrid import *

def send_message(request):
    name = "Joe Lennon"
    sent_date = datetime.datetime.now()
    #/Users/chengmin/PycharmProjects/DjangoProject2ForHuaWei/templates
    #return render_to_response(os.getcwd()+'/templates/U1.html', locals())
    return render_to_response('U1.html', locals())

