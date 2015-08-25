__author__ = 'chengmin'
import fim,os
#with open(os.getcwd()+'/APRIORIREADME.TXT',"w")as fout:
    #fout.write(fim.apriori.__doc__)
    #fout.write(str(help(fim.apriori)))
    #fout.write(fim.apriori)
fin=open("FIMtest").read()
print(fim.apriori(fin))