__author__ = 'chengmin'
'''
Implement AprioriTID algorithm with associated apriori-gen function to generate candidate large itemsets
from Agrawal's 'Fast Algorithms for Mining Association Rules'
'''
import itertools
import sys
from common import *
import os
#Generate all k size large itemsets, those with minimum support.
#Return Ck where each member has two fields: i) itemset ii) support count
#assumes itemset in Lk-1 is sorted
def aprioriGen(LkminusOne, k):
    LkminusOneSets=[]
    kminus = int(k-1)
    lenCK=0
    lenCKprune=0
    Ck=[] #list{ tuple([sorted large itemset],support) }
    prunedCk = []
    if k==2: #trivial case
        for i in range(len(LkminusOne)):
            for j in range(len(LkminusOne)-i-1):
                #assume candidate set support is at most min support of each
                tempList=[LkminusOne[i][0],LkminusOne[j+i+1][0]] #UNSORTED
                tempTuple=tuple( (tempList, min(LkminusOne[i][1],LkminusOne[j+i][1])) )
                # print tempTuple
                prunedCk.append(tempTuple)
    elif k>2:
        #convert LkminusOne to list of sets for easier comparisons later
        for i in range(len(LkminusOne)):
            LkminusOneSets.append(set(LkminusOne[i][0]))


        #creates sets from the prefix of each LkminusOne itemset
        for i in range(len(LkminusOne)):
            # print i
            tempSet1=set(LkminusOne[i][0][0:k-2]) #generate prefix of LkminusOne itemset

            for j in range(len(LkminusOne)-i-1):
                tempSet2=set(LkminusOne[j+i+1][0][0:k-2]) #genereate another prefix
                '''
                print 'tempset1 {}'.format(tempSet1)
                print 'tempset2 {}'.format(tempSet2)
                print ''
                print 'last element from 1: {}'.format(LkminusOne[i][0][-1])
                print 'last element from 2: {}'.format(LkminusOne[j+i+1][0][-1])
                '''
                #compare prefixes of each itemset from LkminusOne
                if len(tempSet2 & tempSet1)==(k-2) and LkminusOne[i][0][-1] != LkminusOne[j+i+1][0][-1]: #if theyre equal except for last element
                    #print LkminusOne[i][0][:]
                    #print LkminusOne[j+i+1][0][:]
                    tmpList1=list(LkminusOne[i][0]) #construct by copy
                    #print 'TMPLIST1: {}'.format(tmpList1)
                    tmpList1.append(LkminusOne[j+i+1][0][-1]) #UNSORTED k size candidate itemset
                    tempList=list(tmpList1)
                    #print 'TEMPLIST: {}'.format(tempList)
                    tempTuple=tuple( (tempList, min(LkminusOne[i][1], LkminusOne[j+i+1][1])) )
                    #print 'TEMP TUPLE: {}'.format(tempTuple)
                    Ck.append(tempTuple)
        lenCK=len(Ck)
        #PRUNE STEP
        #Delete all itemsets c in Ck s.t. some (k-1) subset of c is not in Lk-1

        for i in range(len(Ck)):
            s=set(Ck[i][0])
            # print 'set: {} k: {}'.format(s,kminus)
            setList=map(set, itertools.combinations(s,kminus))  #generate all k-1 combinations of each candidate itemset
            # print 'SetList: {}'.format(setList)
            deleteCandidate = False
            for j in range(len(setList)):
                # print j
                count = 0
                for k in range(len(LkminusOneSets)):

                    if len(setList[j] & LkminusOneSets[k]) != len(LkminusOneSets[k]):
                        count = count + 1
                if count == len(LkminusOneSets): #candidate itemset subset not found in any of prior Lk-1, DISCARD entire candidate with short circuit
                    deleteCandidate = True
                    break

            if not deleteCandidate:
                prunedCk.append(Ck[i])

        lenCKprune = len(prunedCk)
        # print 'old length: {} pruned length: {}'.format(lenCK, lenCKprune)
    return prunedCk




#generate k=1 size large itemsets
#input a list of lists corresponding to transactions. This is the in-memory
#representation of a database table of transactions
def LargeItemsetGen(transactions,minsupp):
    #keep each unique item found during linear pass through Transactions
    #in a dictionary along with count
    transTotal=len(transactions)
    L1=[]
    dictRawItem = {}
    for tid in range(transTotal):
        items = transactions[tid][1]

        for i in range(len(items)):
            if str(items[i]).lower().strip() == "unspecified" or \
               str(items[i]).lower().strip() == "n/a" or str(items[i]).strip() == "":
                continue

            if items[i] in dictRawItem:
                dictRawItem[items[i]] =  dictRawItem[items[i]] + 1
            else:
                dictRawItem[items[i]] = 1

    #extract large itemsets having minsupport and place into L1=list{ tuple([sorted large itemset],support) }
    for key in dictRawItem:
        support = float(dictRawItem[key])/transTotal
        if support >= minsupp:
            #add item to L1
            L1.append(tuple((key, dictRawItem[key]))) #key , support count
    return  (L1, dictRawItem)


def aprioriTid(transactions, minsupp):
    '''
    Computes large itemsets appropriate for rule mining (which support > minsupp)
    Returns tuple (largesets, supportCounts)
        * supportCounts is the map: itemset => number of occurances in database
        * largesets is a list of itemsets
    '''

    # Initial values
    (L1, item_counts) = LargeItemsetGen(transactions, minsupp)
    prevC_comp = len(transactions)
    prevC_comp2=transactions
    k = 2
    supportCounts = item_counts
    L = [ [],  L1]

    while len(L[k-1]) > 0:

        # Compulte Candidate elements using a-priori gen algorithm
        Ck = aprioriGen(L[k-1], k)
        C_comp = {}

        # For every transaction in previous iteration C'
        for tid in range(prevC_comp):
            if k == 2:
                t_set_of_items = [[x] for x in prevC_comp2[tid][1]]
            else:
                t_set_of_items = prevC_comp2[tid][1]

            Ct = []
            for c in Ck:
                # Determine if this itemset satisfies the condition to be appeneded to Ct
                # that is: { (c- c[k]) in  t.set-of-itemsets  ^ (c- c[k - 1]) in t.set-of-itemsets) }
                c_items = c[0]
                c_items_minus_ck = [list(set(c_items) - set([c_items[k-1]]))]
                c_items_minus_ckminus1 = [list(set(c_items) - set([c_items[k-2]]))]


                ck_belongs_to_t = True
                for item in c_items_minus_ck:

                    if item not in t_set_of_items:
                        ck_belongs_to_t = False

                ckm1_belongs_to_t = True
                for item in c_items_minus_ckminus1:
                    if item not in t_set_of_items:
                        ckm1_belongs_to_t = False

                if ckm1_belongs_to_t and ck_belongs_to_t:
                    Ct.append(list(c_items))

            for c in Ct:
                hashed_set = hash_set(c)
                if hashed_set not in supportCounts:
                    supportCounts[hashed_set] = 0

                supportCounts[hashed_set] += 1

            # If Ct is non-empty, add to C'
            if len(Ct) > 0:
                C_comp[tid] = tuple((tid, Ct))


        # Compute Lk
        L.append([]) # This will be L[k]

        for c in Ck:
            c_items = c[0]
            if hash_set(c_items) not in supportCounts:
                continue
            support = float(supportCounts[hash_set(c_items)])/len(transactions)
            if support >= minsupp:
                L[k].append(tuple((c_items, supportCounts[hash_set(c_items)])))

        # Prepare for next iteration
        prevC_comp = C_comp
        k = k + 1


    # Union of L items excluding last one
    # (first one is excluded as well because it's only a placeholder to adjust starting index)
    result = []
    i = 0

    for l in L:
        if i == 0 or i == k - 1:
            i += 1
            continue
        i += 1

        result = result + l

    # Retrun
    return (result, supportCounts)

def dataFromFile(fname):
    """Function which reads from the file and yields a generator"""
    file_iter = open(fname, 'rU')
    for line in file_iter:
        #print(line)
        line = line.strip().rstrip(',')                         # Remove trailing comma
        record = frozenset(line.split(','))
        yield record
def getItemSetTransactionList(data_iterator):
    transactionList = list()
    itemSet = set()
    for record in data_iterator:
        transaction = frozenset(record)
        transactionList.append(transaction)
        for item in transaction:
            itemSet.add(frozenset([item]))              # Generate 1-itemSets
    return itemSet, transactionList

#inFile=dataFromFile(os.getcwd()+"/test.csv")
#itemSet, transactionList = getItemSetTransactionList(inFile)
#print(transactionList)
transactionList=[[0,['I1','I3','I4']],[1,['I2','I3','I5']],[2,['I1','I2','I3','I5']],[3,['I2','I5']]]
minSupport=0.15
aprioriTid(transactionList,minSupport)

