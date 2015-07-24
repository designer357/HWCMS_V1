__author__ = 'chengmin'
import re,os
def my_cmp(v1,v2):
    p = re.compile("(\d+)")
    d1 = [int(i) for i in p.findall(v1)][0]
    d2 = [int(i) for i in p.findall(v2)][0]
    print("vvvvv")
    print(d1)
    print(d2)
    print(cmp(d1, d2))
    return cmp(d1, d2)
filelist=os.listdir(os.getcwd()+'/data')
print(filelist)
l = [ 'ch9.txt', 'ch10.txt', 'ch1.txt', 'ch3.txt', 'ch11.txt' ]
filelist=sorted(filelist,my_cmp)
print(sorted(l,my_cmp))
print(filelist)
#print(list(l.sort(my_cmp)))
print(os.path.join(os.path.dirname(__file__)))
print(__file__)

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    return "Hello World"
