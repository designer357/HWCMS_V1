# Hierarchical Agglomerative Cluster Analysis
#
# Copyright (C) 2013 Folgert Karsdorp
# Author: Folgert Karsdorp <fbkarsdorp@gmail.com>
# URL: <https://github.com/fbkarsdorp/HAC-python>
# For licence information, see LICENCE.TXT

from __future__ import division
from __future__ import absolute_import

__author__ = 'chengmin'

#This is the interface for extracting the commands
import os
from attributeExtraction import commandsMatch
import collections
#import tfidf
import numpy
from numpy import *
import numpy as np
import random
import os
import csv
import math
import numpy
import copy
import argparse

from operator import itemgetter
from collections import defaultdict
from itertools import combinations, product

from api import AbstractClusterer
from dendrogram import Dendrogram
from linkage import linkage_fn
from distance import *

from sklearn.metrics.pairwise import pairwise_distances



class CooccurrenceMatrix(numpy.ndarray):
    """ Represents a co-occurrence matrix. """
    def __new__(cls, data, dtype=None):
        if not isinstance(data, CooccurrenceMatrix):
            data, rownames, colnames = CooccurrenceMatrix.convert(data)
        else:
            rownames, colnames = data.rownames, data.colnames
        obj = numpy.asarray(data).view(cls)
        obj.rownames = rownames
        obj.colnames = colnames
        return obj

    def __array_finialize__(self, obj):
        if obj is None: return
        self.rownames = getattr(obj, 'rownames', None)
        self.colnames = getattr(obj, 'colnames', None)

    def row(self, row):
        return self[self.rownames.get(row)]

    def col(self, col):
        return self[:,self.colnames.get(col)]

    def cell(self, row, col):
        return self[self.rownames.get(row), self.colnames.get(col)]

    @classmethod
    def convert(cls, data):
        matrix = numpy.zeros((len(set(k for k,v in data)),
                              len(set(v for k,v in data))))
        colnames, rownames = {}, {}
        for k,v in sorted(data):
            if k not in rownames:
                rownames[k] = len(rownames)
            if v not in colnames:
                colnames[v] = len(colnames)
            matrix[rownames[k],colnames[v]] += 1
        #rownames = [k for k,v in sorted(rownames.items(), key=itemgetter(1))]
        #colnames = [k for k,v in sorted(colnames.items(), key=itemgetter(1))]
        return matrix, rownames, colnames

    def tfidf(self):
        """
        Returns a matrix in which for all entries in the co-occurence matrix
        the 'term frequency-inverse document frequency' is calculated.
        """
        matrix = numpy.zeros(self.shape)
        # the number of words in a document
        words_per_doc = numpy.asarray(self.sum(axis=1), dtype=float)
        # the number of documents in which a word is attested.
        word_frequencies = numpy.asarray(numpy.sum(self > 0, axis=0), dtype=float)
        # calculate the term frequencies
        for i in range(self.shape[0]):
            tf = self[i] / words_per_doc[i] # array of tf's
            matrix[i] = tf * (numpy.log(self.shape[0] / word_frequencies))
        return matrix


class DistanceMatrix(numpy.ndarray):
    """
    Simple wrapper around numpy.ndarray, to provide some custom
    Distance Matrix functionality like plotting the distance matrix
    with matplotlib.
    """
    def __new__(cls, data, dist_metric=euclidean_distance, lower=True):
        if (not isinstance(data, (numpy.ndarray, DistanceMatrix))
            or len(data) != len(data[0])
            or not max(numpy.diag(data)) == 0):
            data = DistanceMatrix.convert_to_distmatrix(data, dist_metric, lower=lower)
        obj = numpy.asarray(data).view(cls)
        obj.distance_metric = dist_metric
        return obj

    def __array_finialize__(self, obj):
        if obj is None: return
        self.distance_metric = getattr(obj, 'distance_metric', None)

    def row(self, row):
        return self[self.rownames.get(row)]

    def col(self, col):
        return self[:,self.colnames.get(col)]

    def cell(self, row, col):
        return self[self.rownames.get(row), self.colnames.get(col)]

    def rows(self):
        return [k for k,v in sorted(self.rownames.items(), key=itemgetter(1))]

    @classmethod
    def convert_to_distmatrix(cls, data, distance, lower=True):
        matrix = numpy.zeros((len(data), len(data)))
        for i,j in combinations(range(len(data)), 2):
            matrix[i][j] = distance(data[i], data[j])
            if lower == True:
                matrix[j][i] = matrix[i][j]
        # add a nan-diagonal, useful for further computations.
        numpy.fill_diagonal(matrix, numpy.nan)
        return matrix

    def diag_is_zero(self):
        """Check if the diagonal contains only distances of 0."""
        return max(numpy.diag(self)) == 0

    def remove(self, idx):
        """
        Delete a row and column with index IDX.
        WARNING this function is NOT destructive!
        """
        indices = range(len(self))
        indices.remove(idx)
        return self.take(indices, axis=0).take(indices, axis=1)

    def draw(self, save=False, format="pdf"):
        """Make a nice colorful plot of the distance matrix."""
        try:
            import pylab
        except ImportError:
            raise ImportError("Install pylab.")
        fig = pylab.figure()
        axmatrix = fig.add_axes([0.1,0.1,0.8,0.8])
        im = axmatrix.matshow(self, aspect='auto', origin='upper',
                              cmap=pylab.cm.YlGnBu)
        axcolor = fig.add_axes([0.91, 0.1, 0.02, 0.8])
        pylab.colorbar(im, cax=axcolor)
        fig.show()
        if save:
            fig.savefig('distance-matrix.%s' % (format,))

    def summary(self):
        """Return a small summary of the matrix."""
        print('DistanceMatrix (n=%s)' % len(self))
        print('Distance metric = %s' % self.distance_metric.__name__)
        print(self)


class Clusterer(AbstractClusterer):
    """
    The Hierarchical Agglomerative Clusterer starts with each of the N vectors
    as singleton clusters. It then iteratively merges pairs of clusters which
    have the smallest distance according to function LINKAGE. This continues
    until there is only one cluster.
    """
    def __init__(self, data, linkage='ward', num_clusters=1):
        self._num_clusters = num_clusters
        vector_ids = [[i] for i in range(len(data))]
        self._dendrogram = Dendrogram(vector_ids)
        numpy.fill_diagonal(data, numpy.inf)
        self._dist_matrix = data
        self.linkage = linkage_fn(linkage)

    def smallest_distance(self, clusters):
        """
        Return the smallest distance in the distance matrix.
        The smallest distance depends on the possible connections in
        the distance matrix.

        @param clusters: an object of the class L{DistanceMatrix} holding the
            clusters at a specific state in the clustering procedure.
        @type clusters: L{DistanceMatrix}
        @return: a tuple containing the smallest distance and the indexes of
            the clusters yielding the smallest distance.
        """
        i, j = numpy.unravel_index(numpy.argmin(clusters), clusters.shape)
        return clusters[i, j], i, j

    def cluster(self, verbose=0, sum_ess=False):
        """
        Cluster all clusters hierarchically until the level of
        num_clusters is obtained.

        @param verbose: how much output is produced during the clustering (0-2)
        @type verbose: C{int}

        @return: None, desctructive method.
        """
        ## if sum_ess and self.linkage.__name__ != "ward_link":
        ##     raise ValueError(
        ##         "Summing for method other than Ward makes no sense...")
        clusters = copy.copy(self._dist_matrix)
        #clusters = self._dist_matrix
        summed_ess = 0.0

        while len(clusters) > max(self._num_clusters, 1):
            if verbose >= 1:
                print('k=%s' % len(clusters))
                if verbose == 2:
                    print(clusters)

            best, i, j = self.smallest_distance(clusters)
            # In Ward (1963) ess is summed at each iteration
            # in R's hclust and Python's hcluster and some text books it is not.
            # Here it is optional...
            if sum_ess:
                summed_ess += best
            else:
                summed_ess = best
            clusters = self.update_distmatrix(i, j, clusters)
            self._dendrogram.merge(i,j)
            self._dendrogram[i].distance = summed_ess
            indices = numpy.arange(clusters.shape[0])
            indices = indices[indices!=j]
            clusters = clusters.take(indices, axis=0).take(indices, axis=1)

    def update_distmatrix(self, i, j, clusters):
        """
        Update the distance matrix using the specified linkage method so that
        it represents the correct distances to the newly formed cluster.
        """
        return self.linkage(clusters, i, j, self._dendrogram)

    @property
    def dendrogram(self):
        """Return the dendrogram object."""
        return self._dendrogram

    def num_clusters(self):
        return self._num_clusters

    def __repr__(self):
        return """<Hierarchical Agglomerative Clusterer(linkage method: %r,
                  n=%d clusters>""" % (self.linkage.__name__, self._num_clusters)


class VNClusterer(Clusterer):
    """
    Variability Neighbor Clustering Class. A subclass of the regular Clusterer
    where the order of clustering can be predetermined. In the normal clustering
    procedure, all clusters can be clustered with all other clusters. In this
    class, the clusters that are allowed to be clustered follow a specific order.
    """
    def __init__(self, data, linkage='ward', num_clusters=1):
        Clusterer.__init__(self, data, linkage, num_clusters=num_clusters)

    def iterate_clusters(self, clusters):
        for i in range(1, len(clusters)):
            yield i-1,i

    def smallest_distance(self, clusters):
        best = None
        for i, j in self.iterate_clusters(clusters):
            if best is None or clusters[i][j] <= best[0]:
                best = (clusters[i][j], i, j)
        return best

    def cluster(self, verbose=False):
        # we must sum the error sum of squares in order not to obtain
        # singleton clustering.
        Clusterer.cluster(self, verbose=verbose, sum_ess=True)


class EuclideanNeighborClusterer(VNClusterer):

    def iterate_clusters(self, x, y):
        n_features, n_samples = x, y
        offset = (0, -1, 1)
        indices = ((i, j) for i in range(n_features) for j in range(n_samples))
        for i, j in indices:
            all_neigh = ((i + x, j + y) for x in offset for y in offset)
            valid = ((i*n_features + j) for i, j in all_neigh if (0 <= i < n_features) and (0 <= j < n_samples))
            target = valid.next()
            for neighbor in list(valid):
                yield target, neighbor

def demo(Input,labels):
    """
    Demo to show some basic functionality.
    """
    # declare dummy input vector with two dimensions:
    #vectors = numpy.array([[2,4], [0,1], [1,1], [3,2], [4,0], [2,2], [8, 9], [8, 11]])
    vectors=Input
    print(Input)
    # compute the distance matrix on the basis of the vectors via sklearn:
    #dist_matrix = pairwise_distances(vectors, metric='cityblock')
    dist_matrix = pairwise_distances(vectors, metric='euclidean')

    # plot the distance matrix:
    # dist_matrix.draw() this doesn't work anymore

    # initialize a temporal VNC clusterer, here with the Ward linkage method:
    #clusterer = VNClusterer(dist_matrix, linkage='ward') # could also be a plain Clusterer()
    #clusterer = VNClusterer(dist_matrix, linkage='centroid') # could also be a plain Clusterer()
    #clusterer = VNClusterer(dist_matrix, linkage='median') # could also be a plain Clusterer()
    clusterer = VNClusterer(dist_matrix, linkage='single') # could also be a plain Clusterer()
    #clusterer = VNClusterer(dist_matrix, linkage='complete') # could also be a plain Clusterer()
    #clusterer = VNClusterer(dist_matrix, linkage='average') # could also be a plain Clusterer()

    # start the clustering procedure:
    clusterer.cluster(verbose=1)

    #labels = ['n'+str(i+1) for i in range(len(vectors))]
    # plot the result as a dendrogram
    #clusterer.dendrogram.draw(save=True,
                                #labels=labels,
                                #title="VNC Analysis (Ward's Linkage)")
    clusterer.dendrogram.draw(save=True,
                                labels=labels,
                                title="hierarchical clustering/NMF(K=5)")




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
        # normalizing the dictionary
        #length = float(len(list_of_words))
        tempcount=[]
        for each in set(list(list_of_words)):
            tempcount.append(list_of_words.count(each))

        #print(tempcount)
        length=max(tempcount)
        #print("hahahhahahah......."+str(length))
        #print(doc_dict)
        for k in term_freq:
            term_freq[k] = term_freq[k] / length#tf




        # add the normalized document to the corpus
        self.documents.append([doc_name, term_freq])
    def GetTfIdf(self):
        TF_IDF=[[] for tab1 in range(len(self.documents))]
        #for tab1 in range(len(self.corpus_dict)):
        #TF_IDF.append([])
        WordList=sorted(list(self.corpus_dict))

        for tab1 in range(len(self.documents)):
            for tab2 in range(len(self.corpus_dict)):
                TF_IDF[tab1].append(0)
        for i in range(len(self.documents)):
            for k,v in self.documents[i][1].items():
                if k in self.corpus_dict:
                    j = WordList.index(k)
                    TF_IDF[i][j] = v*math.log(len(self.documents)/float(self.corpus_dict[k]))
                else:
                    pass

        return TF_IDF

def matrix_factorisation(R, K, steps=5000, alpha=0.0002, beta=0.02):
    N = len(R)
    M = len(R[0])

    P = numpy.random.rand(N,K)
    Q = numpy.random.rand(M,K)
    #print(Q)
    Q = Q.T
    #print(Q)
    for step in xrange(steps):
        for i in xrange(len(R)):
            for j in xrange(len(R[0])):
                #print(R[j])
                if R[i][j] > 0:
                    eij = R[i][j] - numpy.dot(P[i,:],Q[:,j])
                    for k in xrange(K):
                        #print(P[k])
                        #print(Q[k][j])
                        #print(eij)
                        P[i][k] = P[i][k] + alpha * (2 * eij * Q[k][j] - beta * P[i][k])
                        Q[k][j] = Q[k][j] + alpha * (2 * eij * P[i][k] - beta * Q[k][j])
        eR = numpy.dot(P,Q)
        e = 0
        for i in xrange(len(R)):
            for j in xrange(len(R[0])):
                if R[i][j] > 0:
                    e = e + pow(R[i][j] - numpy.dot(P[i,:],Q[:,j]), 2)
                    for k in xrange(K):
                        e = e + (beta/2) * (pow(P[i][k],2) + pow(Q[k][j],2))
        if e < 0.001:
            break
    return P, Q.T
def NMF_Cluster(v,k):
    w,h = matrix_factorisation(v,k)
    print(w.shape)

    cluster = [[] for i in range(k)]
    #ht = transpose(h)
    ht=w

    #print(shape(ht)[0])
    #print(shape(ht)[1])
    #print(ht)
    for i in range(shape(ht)[0]):
        bestlabel = 0
        max_eig = 0
        for j in range(shape(ht)[1]):
            if ht[i,j] > max_eig:
                max_eig = ht[i,j]
                bestlabel = j
        cluster[bestlabel].append(i)
    return cluster
def countCommands(filePath):
    return(commandsMatch(filePath))


def cluster_points(X, mu):
    clusters  = {}
    clusters_index  = {}

    #for x in X:
    for tab in range(len(X)):
        bestmukey = min([(i[0], np.linalg.norm(X[tab]-mu[i[0]])) \
                    for i in enumerate(mu)], key=lambda t:t[1])[0]
        try:
            clusters[bestmukey].append(X[tab])
            clusters_index[bestmukey].append(tab)
        except KeyError:
            clusters[bestmukey] = [X[tab]]
            clusters_index[bestmukey] = [tab]
    return clusters,clusters_index

def reevaluate_centers(mu, clusters):
    newmu = []
    keys = sorted(clusters.keys())
    for k in keys:
        newmu.append(np.mean(clusters[k], axis = 0))
    return newmu

def has_converged(mu, oldmu):
    return (set([tuple(a) for a in mu]) == set([tuple(a) for a in oldmu]))

def find_centers(X, K):
    # Initialize to K random centers
    oldmu = random.sample(X, K)
    mu = random.sample(X, K)
    clusters,clusters_index = cluster_points(X, mu)
    while not has_converged(mu, oldmu):
        oldmu = mu
        # Assign all points in X to clusters
        clusters,clusters_index = cluster_points(X, mu)
        # Reevaluate centers
        mu = reevaluate_centers(oldmu, clusters)
    #print(mu,clusters)
    return(mu, clusters,clusters_index)

#def init_board(N):
   # X = np.array([(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(N)])
   # return X

def eculidsistance(point1,point2):
    distance=0.0
    for tab in range(len(list(point1))):
        distance = distance + pow (point1[tab]-point2[tab],2)
    return math.sqrt(distance)
def find_the_points_near_the_center(centerlist,pointsdict):
    output=[]
    for k,v in pointsdict.items():
        distance=[]
        center=centerlist[int(k)]
        for each in v:
            distance.append(eculidsistance(center,each))
        #print(distance)
        distance2 = sorted(distance)
        #print(distance2)
        output.append(v[distance.index(distance2[0])])
        #print(output)
    return output











"""
R = [
     [5,3,0,1],
     [4,0,0,1],
     [1,1,0,5],
     [1,0,0,4],
     [0,1,5,4],
    ]
R = numpy.array(R)
"""




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
"""

table.addDocument("foo", ["alpha", "alpha","bravo", "charlie"])
#print(table.documents)
#print(table.weighted)
#print(table.corpus_dict)
table.addDocument("bar", ["alpha", "bravo","charlie"])
table.addDocument("bar", ["alpha", "bravo","mike"])
#table.addDocument("baz", ["kilo", "lima", "mike", "november"])
#print table.similarities (["alpha", "bravo"])
print(table.GetTfIdf())
"""



"""
K = 5
nP, nQ = matrix_factorisation(R, K)
nR = numpy.dot(nP, nQ.T)
#output=NMF_Cluster(R,K)
print(nR)
#print(output)
#print(R)
N=9
C1,C2,C3=find_centers(R,N)
print(C1)
print(C2)
print(C3)
for k,v in C3.items():
    for e in range(len(v)):
        v[e] = Lebel[v[e]]
print(C3)
for each in table.documents:
    print(each)
for each in table.GetTfIdf():
    print(each)
#output=find_the_points_near_the_center(C1,C2)
"""

"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, dendrogram

data_dist = pdist(R) # computing the distance
data_link = linkage(data_dist) # computing the linkage

dendrogram(data_link,labels=Lebel_index)
plt.xlabel('Samples')
plt.ylabel('Distance')
plt.suptitle('Samples clustering', fontweight='bold', fontsize=14)
plt.show()

"""

if __name__ == '__main__':
    from numpy import *
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import linkage
    from scipy.cluster.hierarchy import dendrogram
    #mat = array([[1, 0.5, 0.9],
             #[0.5, 1, -0.5],
             #[0.9, -0.5, 1]])




    table = tfidf()
    inputPath="ServerData2"
    GetAllTF_IDF(inputPath)
    Lebel=[]
    Lebel_index=[]
    count=0
    for t in table.documents:
        Lebel.append(t[0])
        Lebel_index.append(count)
        count += 1



    print(Lebel)



    A=numpy.array(table.GetTfIdf())
    #print(A)
    #B=A.T
    R=A
    K = 5
    nP, nQ = matrix_factorisation(R, K)



    #plt.subplot(1,2,1)
    #plt.title("hierarchical clustering TF-IDF")
    #dist_mat = R#nP
    plt.title("hierarchical clustering NMF("+str(K)+")")
    dist_mat = nP
    linkage_matrix = linkage(dist_mat,"single")
    #print "linkage2:"
    #print linkage(1-dist_mat, "single")
    dendrogram(linkage_matrix,color_threshold=1,orientation="right",labels=Lebel,show_leaf_counts=False)
    plt.show()
    #demo(nP,Lebel_index)

    """
    inPut = array([[2,4], [0,1], [1,1], [3,2], [4,0], [2,2], [8, 9], [2, 4]])
    Lebel_index=[]
    count=0
    for t in inPut:
        Lebel_index.append(count)
        count += 1
    demo(inPut,Lebel_index)
    """


