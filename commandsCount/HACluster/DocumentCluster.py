__author__ = 'chengmin'
# Router Document Hierarchical Agglomerative Cluster Analysis Based on TF-IDF&NMF
# For Misconfiguration Detection
# Copyright (C) 2015 City University of Hong Kong
# Author: Cheng Min <designer357@hotmail.com>
# URL: <https://github.com/designer357/>
from numpy import *
import numpy as np
import os
import math
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram

#Read All Contents From Files
def readLibrary(path):
    f = open(path)
    commandList = []
    for lines in f:
        commandList.append(lines.strip())
    return(commandList)
def findAllIndex(longStr, subStr):
    i = 0
    l = len(longStr)
    s = len(subStr)
    offsetList = []
    while(i < l and longStr[i:].find(subStr) != -1):
        offsetList.append(i + longStr[i:].find(subStr))
        i = offsetList[-1]+s
    return(offsetList)

def commandsMatch(filePath):
    #The txt should be placed at the same folder
    commandList = readLibrary('AllCommandersOutput.txt')
    occurredCommand = []
    f = open(filePath)
    count=0
    for lines in f:
        count += 1
        commandDict1 = dict()
        commandDict2 = dict()
        for command in commandList:
            offsetList = findAllIndex(lines, command)
            length = len(command)
            if(len(offsetList) > 0):
                for offset in offsetList:
                    if(offset == 0 and (lines[length] == ' ' or lines[length] == '\n')):
                        if(offset in commandDict1.keys()):
                            commandDict1[offset].append(command)
                        else:
                            commandDict1[offset] = []
                            commandDict1[offset].append(command)

                    elif(offset > 0 and lines[offset-1] == ' ' and (lines[offset + length] == ' ' or lines[offset + length] == '\n')):
                        if(len(commandDict2) == 0):
                            commandDict2[offset] = []
                            commandDict2[offset].append(command)
                        else:
                            if(offset in commandDict2.keys()):
                                commandDict2[offset].append(command)
                            else:
                                commandDict2[offset] = []
                                commandDict2[offset].append(command)

        #print(count, commandDict1, commandDict2)
        for keys in commandDict1:
            occurredCommand.append(commandDict1[keys][-1])
        for keys in commandDict2:
            occurredCommand.append(commandDict2[keys][-1])
    #return(list(set(occurredCommand)))
    return(list(occurredCommand))

#Compute the TF-IDF for Document
class tfidf:
    def __init__(self):
        self.weighted = False
        self.documents = []
        self.corpus_dict = {}#idf

    def addDocument(self, doc_name, list_of_words):
        # building a dictionary
        term_freq = {}
        for w in list_of_words:
            term_freq[w] = term_freq.get(w, 0.) + 1.0#tf
        for w in list(set(list_of_words)):
            self.corpus_dict[w] = self.corpus_dict.get(w, 0.0) + 1.0#idf
        #tf_idf[w] = tf_idf.get(w, 0.0)#tf_idf

        # normalizing the term-frequency
        #length = float(len(list_of_words))
        tempcount=[]
        for each in set(list(list_of_words)):
            tempcount.append(list_of_words.count(each))
        length=max(tempcount)
        for k in term_freq:
            term_freq[k] = term_freq[k] / length#tf
        self.documents.append([doc_name, term_freq])
    def GetTfIdf(self):
        print("Computing TFIDF.......")
        #TF_IDF=[[] for tab1 in xrange(len(self.documents))]
        #for tab1 in range(len(self.corpus_dict)):
        #TF_IDF.append([])
        WordList=sorted(list(self.corpus_dict))
        m=len(self.documents)
        n=len(self.corpus_dict)
        #for tab1 in xrange(len(self.documents)):
            #for tab2 in xrange(len(self.corpus_dict)):
                #TF_IDF[tab1].append(0)
        TF_IDF=np.zeros((m,n))
        for i in xrange(m):
            print(str(self.documents[i])+"is processing......")
            for k,v in self.documents[i][1].items():
                if k in self.corpus_dict:

                    j = WordList.index(k)
                    print(str(j)+"_________________"+str(i))
                    TF_IDF[i][j] = v*math.log(m/float(self.corpus_dict[k]))#idf
                else:
                    pass
        print("Completed!")

        return TF_IDF
#Non-Negative Matrix Factorisation
def matrix_factorisation(R, K, steps=5000, alpha=0.0002, beta=0.02):
    print("Computing NMF......")
    N = len(R)
    M = len(R[0])
    P = np.random.rand(N,K)
    Q = np.random.rand(M,K)
    Q = Q.T
    for step in range(steps):
        for i in range(len(R)):
            for j in range(len(R[0])):
                print("11")
                if R[i][j] > 0:
                    eij = R[i][j] - np.dot(P[i,:],Q[:,j])
                    for k in range(K):
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = np.dot(P,Q)
        e = 0
        for i in range(len(R)):
            for j in range(len(R[0])):
                if R[i][j] > 0:
                    print("22")
                    e = e + pow(R[i][j] - np.dot(P[i,:],Q[:,j]), 2)
                    for k in range(K):
                        e = e + (beta/2) * (pow(P[i][k],2) + pow(Q[k][j],2))
        if e < 0.001:
            break
    return P, Q.T

def countCommands(filePath):
    return(commandsMatch(filePath))

def GetAllTF_IDF(inputPath):
    filefolderpath=os.path.join(os.getcwd(),inputPath)
    #WordDict=collections.defaultdict(int)
    for eachfile in os.listdir(filefolderpath):
        if '.DS_Store' in eachfile:
        #if not '.ha' in eachfile:
            continue
        print("adding "+eachfile)
        L=countCommands(os.path.join(filefolderpath,eachfile))
        table.addDocument(eachfile,L)


if __name__ == '__main__':
    #Please Input The Folder Name
    #---------------------------------------------------------->
    inputPath="ServerData2"
    #----------------------------------------------------------|

    table = tfidf()
    GetAllTF_IDF(inputPath)
    Label=[]
    Label_index=[]
    count=0
    for t in table.documents:
        Label.append(t[0])
        Label_index.append(count)
        count += 1

    R=np.array(table.GetTfIdf())
    #R=np.matrix(table.GetTfIdf())

    if 1>0:
        #hierarchical clustering based on TF-IDF
        print("11111111111111111")
        plt.title("hierarchical clustering TF-IDF")
        print("11111111111111112")
        dist_mat = R
        print("11111111111111113")
        linkage_matrix = linkage(dist_mat,"single")
        print("11111111111111114")
        dendrogram(linkage_matrix,color_threshold=1,orientation="right",labels=Label,show_leaf_counts=True)
        print("11111111111111115")
        plt.savefig('hierarchical clustering TF-IDF.pdf',dpi = 200)

        #plt.show()
        plt.clf()
        print("222222222222222222")
        #hierarchical clustering based on NMF
        K = 5#The Number of Potential Features
        nP, nQ = matrix_factorisation(R, K)

        plt.title("hierarchical clustering NMF("+str(K)+")")
        dist_mat = nP
        linkage_matrix = linkage(dist_mat,"single")
        dendrogram(linkage_matrix,color_threshold=1,orientation="right",labels=Label,show_leaf_counts=True)
        plt.savefig("hierarchical clustering NMF("+str(K)+").pdf",dpi = 200)

        plt.show()
        print("33333333333333333333")

    else:
        #hierarchical clustering based on TF-IDF
        plt.title("hierarchical clustering TF-IDF")
        dist_mat = R
        linkage_matrix = linkage(dist_mat,"single")
        dendrogram(linkage_matrix,color_threshold=1,orientation="right",labels=Label_index,show_leaf_counts=True)
        plt.savefig('hierarchical clustering TF-IDF.pdf',dpi = 200)

        plt.show()
        plt.clf()

        #hierarchical clustering based on NMF
        plt.title("hierarchical clustering NMF("+str(K)+")")
        dist_mat = nP
        linkage_matrix = linkage(dist_mat,"single")
        dendrogram(linkage_matrix,color_threshold=1,orientation="right",labels=Label_index,show_leaf_counts=True)
        plt.savefig("hierarchical clustering NMF("+str(K)+").pdf",dpi = 200)
        plt.show()

        with open(os.path.join(os.getcwd(),"Label_Index"),"w")as fout:
            for tab in range(len(Label)):
                fout.write(str(Label_index[tab]))
                fout.write("\t:\t"+str(Label[tab])+"\n")

"""
R = [
     [5,3,0,1],
     [4,0,0,1],
     [1,1,0,5],
     [1,0,0,4],
     [0,1,5,4],
    ]
A=np.matrix(R)
K=5
nP, nQ = matrix_factorisation(A, K)
"""

