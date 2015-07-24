#-*- coding:utf-8 -*-
import copy
import re
import time
import resource
import os
#import SelectSession

class Item:
    elements=[]#初始化集合
    supp=0.0#支持度初始化为0
    def __init__(self,elements,supp=0.0):
        self.elements = elements
        self.supp = supp
    def __str__(self):
        returnstr = '[ '
        for e in self.elements:
            returnstr += e+','
        returnstr+=' ]'+' (support :%.3f)\t' %(self.supp)
        return returnstr
    def getSubset(self,k,size):#该函数获取n阶subset
        subset=[]
        if k == 1:#一截
            for i in range(size):
                subset.append([self.elements[i]])
            return subset 
        else:
            i = size - 1        
            while i >= k-1 :
                myset = self.getSubset(k-1,i)
                j = 0
                while j < len(myset):
                    #Attention a+=b  a=a+b  
                    myset[j] +=  [self.elements[i]]   #Why Elements change here?
                    j += 1
                subset += (myset)
                i -= 1
            return subset
        
    def lastDiff(self,items):
        length = len(self.elements)
        if length != len(items.elements):#length should be the same
            return False
        if self.elements == items:#if all the same,return false
            return False
        return self.elements[0:length-1] == items.elements[0:length-1]
    def setSupport(self,supp):
        self.supp = supp
        
    def join(self,items):
        temp = copy.copy(self.elements)
        temp.insert(len(self.elements), items.elements[len(items.elements) - 1])
        it = Item(temp,0.0)
        return it
#        self.elements.insert(len(self.elements), items.elements[len(items.elements) - 1])#Wrong,if so ,self.elements will change
#        it = Item(self.elements,0.0)
#        print(self.elements)
#        return it
    
#        the following is Wrong ,Because the Constructor Item(),First par is None
#        return copy.deepcopy(Item(\
#                                  self.elements.insert(\
#                                                       len(self.elements), items.elements[len(items.elements) - 1]\
#                                                       )\
#                                  ,0.0)\
#                             )
class C:
    '''candidate '''
    elements=[]
    k = 0 #order
    def __init__(self,elements,k):
        self.elements = elements
        self.k = k
        
    def isEmpty(self):
        if len(self.elements) == 0:
            return True
        return False
    #get the same order of itemsets whose support is at lease the threshold
    def getL(self,threshold):
        items=[]
        for item in self.elements:
            if item.supp >= threshold:
                items.append(copy.copy(item))
        if len(items) == 0:
            return L([],self.k)
        return L(copy.deepcopy(items),self.k)   
    
    def __str__(self):
        returnstr = str(self.k)+'-itemset:'+str(len(self.elements))+' \r\n{ '
        for e in self.elements:
            if True == isinstance(e,Item):
                returnstr += e.__str__()
        returnstr +=' }'
        return returnstr
    
class L:
    '''store all the  1-itemsets,2-itemsets,...k-itemsets'''
    items=[] #all the item in order K
    k=0  
    def __init__(self,items,k):
        self.items = items
        self.k = k
    def has_inFrequentItemsets(self,item):
#        return False
#        #先不优化
        subs = item.getSubset(self.k, len(item.elements))
        for each in subs:
            flag=False
            for i in self.items:
                if i.elements==each:
                    flag=True
                    break 
            if flag==False:
#                print("remove");print(item)
                return True  
        return False #there is at least one subset in the freq-items
        
    def aprioriGen(self):
        length=len(self.items)
        result=[]
        for i in range(length):
            for j in range(i+1,length):
                if self.items[i].lastDiff(self.items[j]):
                    item = self.items[i].join(self.items[j])
                    if False == self.has_inFrequentItemsets(item):#用Apriori性质：任一频繁项集的所有非空子集也必须是频繁的，反之，如果某个候选的非空子集不是频繁的，那么该候选肯定不是频繁的，从而可以将其从CK中删除。
                        result.append(item)
        if(len(result) == 0):
            return C([],self.k+1)
        #print("AAAAAAAAAAA")
        #print(C(result,self.k+1))
        return C(result,self.k+1)
    
    def __str__(self):
        returnstr="\r\n"+str(self.k) + '-itemsets :'+str(len(self.items))+"\r\n{"
        for item in self.items:
            returnstr += item.__str__()
        returnstr += '}'
        return returnstr
        
class LS:
    '''store from 1-itemset to k-itemset'''
    #values={}#L1,L2,Lk
    def __init__(self):
        self.values={}
    def get(self,k):
        return self.values[k]
    def size(self):
        return len(self.values)
    def put(self,l,k):
        self.values[k]=l
    def isEmpty(self):
        return self.size()==0    
    def __str__(self):
        returnstr = '-----result--------\r\n'
        for l in self.values:
            returnstr += self.values[l].__str__()
        return returnstr
class Rule:
    confidence=.0
    lift=.0
    KULC=.0
    IR=.0
    str_rule=''
    def __init__(self,confidence,lift,KULC,IR,str_rule):
        self.confidence = confidence
        self.lift = lift
        self.KULC = KULC
        self.IR = IR
        self.str_rule = str_rule
    def __str__(self):
        return 'Rule:  %s   confidence:  %3f   lift: %3f   KULC: %3f   IR: %3f' %(self.str_rule,self.confidence,self.lift,self.KULC,self.IR)
      
class Apriori:
    def __init__(self,min_supp=0.07,datafile='apriori.test.data'):
        inputfile = open(datafile,"r")
        self.data=[]
        self.size=0
        self.min_supp = min_supp
        print("Init........")
        for line in inputfile.readlines():
            #linearray = re.compile("[\d]+").findall(line)
            #linearray = re.compile("[\w]+").findall(line)
            #linearray = re.compile("[a-zA-Z\t\d]").findall(line)
            #templinearray=line.split(',')
            linearray=list(filter(lambda a: len(a)>1,line.split(',')))
            for t in range(len(linearray)):
                if '\n' in linearray[t]:
                    linearray[t]=linearray[t].replace('\n','')

            print(linearray)
            if len(list(set(linearray)))>=1:
                self.data.append(list(set(linearray)))
        
        self.size=len(self.data)
        #print(self.size)
        #print(self.data)
        
    def  findFrequent1Itemsets(self):
        totalItemsets=[]
        for temp in self.data:
            totalItemsets.extend(temp)
        items = []#store the 1-itemset s
        
        while len(totalItemsets)>0:
            item=totalItemsets[0]
            count=0 
            j=0
            while j<len(totalItemsets):
                if (item == totalItemsets[j]) :
                    count += 1 
                    totalItemsets.remove(item) #remove the first occurence
                else:
                    j += 1
            t_supp = float(count)/self.size
#            print(t_supp)
            
            if t_supp >= self.min_supp:
                items.append(Item([item],t_supp))
            
        temp = L(copy.deepcopy(items),1)
        #print("The first is")
        #print(temp)
        return   temp
    def ralationRules(self,maxSequence,min_confidence,min_lift,min_kulc,thresh_ir):
        ruls=[]
        for each in maxSequence:
            #print("11111111111"+str(each))
            for i in range(len(each.elements)-1):#real subsets 
                subsets = each.getSubset(i+1,len(each.elements))#get the subsets of the i+1 events
                #print("222222222222222"+str(subsets))
                for subset in subsets:
                    #print("3333333333333333"+str(subset))
                    count1=0
                    for tran_item1 in self.data:
                        flag1 = False #标记subset中的每个元素都在源中出现
                        for ele1 in subset:
                            if ele1 not in tran_item1:
                                flag1=True#subset 中的某个元素没有出现
                                break
                        if flag1 == False: #subset出现一次，计数
                            count1 += 1
                    #print("----------"+str(self.size))
                    #print("44444444444"+str(each))
                    try:
                        confidence = (each.supp*self.size)/count1
                    except:
                        confidence= 0
                    #print(count1/self.size)
                    #print("3333333333333333"+str(subset)+str(confidence))
                    #计算Lift
                    #for subset2 in  set(each.elements)-set(subset):
                    #print("555555555555555"+str(subset)+"##########"+str(set(each.elements)-set(subset)))
                    count2=0
                    for tran_item2 in self.data:
                        flag2 = False #标记subset中的每个元素都在源中出现
                        for ele2 in (set(each.elements)-set(subset)):
                            if ele2 not in tran_item2:
                                flag2=True#subset 中的某个元素没有出现
                                break
                        if flag2 == False: #subset出现一次，计数
                            count2 += 1
                    #lift=confidence/P(B)=P(B|A)/P(B)=P(AB)/P(A)*P(B)
                    #P(AB)=each.supp
                    #P(A)=count1/self.size
                    #P(B)=count2/self.size


                    #KULC=0.5*P(B|A)+0.5*P(A|B)=0.5P(AB)/P(A)+0.5P(AB)/P(B)=0.5P(AB)*(P(A)+P(B))/P(A)P(B)
                    #print("@@@@@@@@@@@@@@@@@"+str(lift))
                    #IR=P(B|A)/P(A|B)=P(B)/P(A)
                    #print("start.........")
                    #print(each.supp)
                    #print(self.size)
                    #print(count1)
                    #print(count2)
                    #print("end............")
                    try:
                        lift=float(confidence)*self.size/count2#lift=confidence/P(B)=P(B|A)/P(B)=P(AB)/P(A)*P(B)
                    except:
                        lift=0
                    try:
                        KULC=0.5*(each.supp)*self.size*(count1+count2)/(count1*count2)
                    except:
                        KULC=0
                    try:
                        IR=count2/count1
                    except:
                        IR=100
                    #try:
                        #IR=abs(count1/self.size-count2/self.size)/abs(count1/self.size-count2/self.size-each.supp)
                    #except:
                        #IR=abs(count1/self.size-count2/self.size)/(abs(count1/self.size-count2/self.size-each.supp)+0.00000000001)
                    #print("start.........")
                    #print(confidence)
                    #print(lift)
                    #print(KULC)
                    #print(IR)
                    #print("end............")
                    if  confidence >= min_confidence and  lift>min_lift and KULC> min_kulc and IR < thresh_ir: #confidence/the number of the frequent pattern
                        str_rule = str(set(subset)) + '-->' + str(set(each.elements)-set(subset))
                        rule =Rule(confidence,lift,KULC,IR,str_rule)
                        ruls.append(rule)
        return ruls
          
    def do(self):      
        ls = LS()
        oneitemset = self.findFrequent1Itemsets()
        ls.put(oneitemset, 1)
        k = 2
        while False == ls.isEmpty():
            cand = ls.get(k - 1).aprioriGen()
            if cand.isEmpty():
                break
            for each in cand.elements:
                count = 0
                for each_src in self.data:
        #            count = each_src.count(each.elements)#only count the single element,can not be used to count if containing more than 2 elements
        #            need a function like Collection.containAll(Collection) in Java
                    if len(each_src)<len(each.elements):
                        pass
                    else:
        #不是必须连续 相等才满足条件，只要元素都在里面即可
        #                for i in range(len(each_src)):
        #                    if each.elements == each_src[i:len(each.elements)]:
        #                         break #no need continue ,We have supposed the elements be sequential
                        flag = True
                        for just_one_e in each.elements:
                                flag = just_one_e in each_src
                                if flag == False: #只要有一个不在，即退出
                                    break
                        if flag == True:   #当前候选事件都在的话，计数     
                            count += 1
                           
                supp = float(count)/self.size
                each.setSupport(supp)
            #print("BBBBBBBBBBBBBB")
            #print(ls)
            ls.put(cand.getL(self.min_supp), k)
            k += 1
            #print(ls)
            #print("The"+str(k)+" itemsets are completed!")
            #print(ls.get(k-1))
        return ls

"""
if not os.path.isdir(os.getcwd()+'/results'):
    os.makedirs(os.getcwd()+'/results')
import InPutForRulesVersion2
filepath=os.getcwd()
interests=["group CONNECTOR {"]
rulesfolder="rules"

starttime = time.time()
timestart = time.clock()

min_supp=0.3
min_cond=0.7
min_lift=0.001
min_kulc=0.001
thresh_ir=10000

for each in interests:
    #InputForRules.GenerateInputForRules(eachgroup)
    with open(os.getcwd()+'/'+rulesfolder+"/output_"+each,"w")as fout:
        pass
    with open(os.getcwd()+"/results/RulesFor_"+each,"w")as fout:
        pass

#time.sleep(3)

for each in interests:
    print(each+"is processing......")
    InPutForRulesVersion2.MainFunc(filepath,each,rulesfolder)
    print(os.getcwd()+'/'+rulesfolder+"/output_"+each)
    a = Apriori(min_supp,os.getcwd()+'/'+rulesfolder+"/output_"+each)
    print(a)
    ls = a.do()
    print(ls)
    rules = a.ralationRules(ls.get(ls.size()).items,min_cond,min_lift,min_kulc,thresh_ir)
    #for rule in rules:
        #print(rule)
    #print(SelectSession.Select)
    with open(os.getcwd()+"/results/RulesFor_"+each,"a")as fout:
        fout.write("min_support is "+str(min_supp)+".  min_confidence is "+str(min_cond)+"\n")
        for rule in rules:
            fout.write(str(rule)+'\n')
        fout.write("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
endtime =  time.time()
time_elapsed = (time.clock() - timestart)
#time_2=endtime-starttime
#print("It takes %f milliseconds to find the above  patterns" %(time_2 * 1000))
#print()
print('耗时：', time_elapsed, 's')

print('内存：', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'byte')
"""