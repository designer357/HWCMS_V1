__author__ = 'chengmin'
import re,os
#import StatisticsALLgroup,InPutForRulesVersion2
import InPutForRulesVersion2
def LoadRules(group):
    with open(os.getcwd()+"/results/RulesFor_"+group)as fin:
        Rules=[[],[]]
        pattern1=re.compile(r'\{.*\}')
        lines=fin.readlines()
        for eachline in lines:
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
#groupList=StatisticsALLgroup.returnAllGroups()
attributesDict,attributesList=InPutForRulesVersion2.returnAttributes()
group="ipv4-family unicast"
rules=LoadRules(group)
print(rules)
print("The number of total rules is "+str(len(rules[0]))+'\n')
#with open("Detected Log.txt","w")as fout:
    #pass

with open("new_bgp_test")as fin:
    for eachline in fin.readlines():
        if len(eachline)>1:
            val=''.join(eachline)
        flag3=-1
        count=0
        tab=0
        while tab <(len(rules[0]))-1:
            tab=tab+1
            #print(str(tab)+'############'+str(flag3))

            flag1=-1
            flag2=-1
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
            if flag1==1 and flag2==0:
                count += 1
                print("Violate the "+str(tab+1)+"th Rule.  The Right form should be :"+str(error_detail1)+"    "+str(error_detail2)+'\n')
                #print("The Error is :  "+str(detected)+'\n')
                #print("The Left of this Error is: "+str(val.count(detected))+'\n')
                with open("Detected Log.txt","a")as fout:
                    fout.write("Violate the "+str(tab+1)+"th Rule.  The Right form should be :"+str(error_detail1)+"    "+str(error_detail2)+'\n')
                    val,detected=replacerightbyerror(rules[0][tab][0]+','+rules[1][tab][0],val)
                    print("The Error is :  "+str(detected))
                    print("The Left of this Error is: "+str(val.count(detected)))
                    #print(rules[0][tab][0]+"-->"+rules[1][tab][0]+'\n')
                    fout.write("The Error is :  "+str(detected)+'\n')
                    fout.write("The Left of this Error is: "+str(val.count(detected))+'\n')
                    flag3=1
                    #tab -= 1
                    fout.write('--------------------------------------------------------------------------------------------------------------------------------\n')
            #else:
                #flag3=-1

print("--------------------------"+str(count)+" rules detected.")
if flag3==-1:
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print(" No Violations.")


