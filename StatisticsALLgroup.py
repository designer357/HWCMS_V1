
__author__ = 'chengmin'
import os,re
def returnAllGroups():
    filelist=os.listdir(os.getcwd())
    ALLGROUP=[]
    for eachfile in filelist:
        if not '.txt' in eachfile and 'bgp_' in eachfile:
            Groups=[]
            pattern=re.compile(r".*group.*#\{")
            linesstr=open(os.path.join(os.getcwd(),eachfile)).read()
            groups=pattern.findall(linesstr)
            for each in groups:
                if ':' in each:
                    pass
                else:
                    val=each.strip().split(' ')
                    Groups.append(val[1])
            Groups=sorted(set(Groups),key=Groups.index)
            ALLGROUP.append(Groups)

    AllGroups=[]
    for each in ALLGROUP:
        for e in each:
            if not e in AllGroups:
                AllGroups.append(e)
    return AllGroups




