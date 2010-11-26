#!/usr/bin/python -OO
# -*- coding: iso-8859-15 -*-

#
# SVG vizualizer.
# http://zvtm.sourceforge.net/zgrviewer/applet/
# http://zvtm.sourceforge.net/zgrviewer.html
#
# http://networkx.lanl.gov/
#>>> import networkx as nx
#>>> G=nx.Graph()
#>>> G.add_node("spam")
#>>> G.add_edge(1,2)
#>>> print(G.nodes())
#[1, 2, 'spam']
#>>> print(G.edges())
#[(1, 2)]
#
# 
# nice icons
# http://www.karakas-online.de/forum/viewtopic.php?t=2647
#
#
#
# http://www.graphviz.org/doc/info/
#

import pHash
from mvptree import MVPTree

import logging,os,re,sys
import networkx as nx
import time, locale

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


'''
find relation between files in a MVP Database
'''
class MVPGraph():
  log=None
  cache=None
  tree=None
  mvpfile=None
  '''
    set ups the graph and the MTP Tree database
  '''
  def __init__(self,dbFilename):
    self.log=logging.getLogger(self.__class__.__name__)
    if (not os.access(dbFilename+'.mvp',os.F_OK)):
      raise IOError("file not found")
    self.tree=MVPTree(dbFilename)
    self.graph=nx.Graph()
    pass
  ''' 
  builf graph from MVP Db 
  '''
  def build(self,dirname):
    myfiles=None
    for root,dirs,files in os.walk(dirname):
      if (root==dirname):
        # make all nodes
        for f in files:
          self.log.debug(" Adding node %s"%(f))
          self.graph.add_node(f)
        myfiles=[os.path.join(root,fname) for fname in files]
    # query edges  
    queryResults=self.tree.queryFiles(myfiles)
    # add edges
    for srcfile,matches in queryResults:
      for match,dist in matches:
        self.log.debug("match : %s , %f"%(match.id,dist))
        tget=os.path.basename(match.id)
        self.log.debug(" tget node : %s"%(tget))
        if tget not in self.graph:
          self.log.warning(" Adding tget node ... weird ... : %s "%(match.id))
          self.graph.add_node(tget)
        # add edge
        self.graph.add_edge(srcfile,tget,{'weight':dist})
    # graph is done
    return
  #      if (len(self.graph.neighbors(dom))>20):
  #        # ignore , yen a trop
  #          self.graph.add_edge(dom,spamurl.url.hostname,{'weight':1})
  def makeGraph(self,filename,graph=None,w=12,h=8):
    if (graph is None):
      graph=self.graph
    # WTF... INCHES !
    self.log.debug('making graph')
    plt.figure(figsize=(w,h))
    self.log.debug('..layout')
    #pos=nx.graphviz_layout(self.graph,prog="twopi",root=0)
    pos=nx.graphviz_layout(graph,prog="neato",root=0)
    nodesSize=[]
    labels={}
    self.log.debug('..nodes')
    # on différencie la taille des node sur leur representation...
    for n in graph.nodes():
      nodesSize.append(50)
      self.log.debug("Label: %s --> %s"%(n,os.path.basename(n)))
      labels[n]=os.path.basename(n)
    #nx.draw_graphviz
    self.log.debug('..draw')
    nx.draw(graph,pos,node_size=nodesSize,labels=labels,alpha=0.7,\
                  font_weight='bold',font_size='12',node_color='y')
    self.log.debug('..write_dot')
    nx.write_dot(graph,''.join([filename,'.dot']))
    self.log.debug('..savefig')
    # extract plt
    plt.savefig(filename)
    return graph




def testGraph(argv):
  
  if len(argv) <3 :
    logging.error('usage: graphmvp.py <dirname> <dbname> <outputgraph>') 
    return 
  
  dirname=argv[0]
  db=argv[1]
  outputfile=argv[2]
  
  g= MVPGraph(db)
  g.build(dirname)
  g.makeGraph(outputfile)



def main(argv):
  '''
  '''
  #locale.setlocale(locale.LC_ALL,'fr_FR')
  logging.basicConfig(level=logging.DEBUG)
  testGraph(argv)



if __name__ == '__main__':
  main(sys.argv[1:])
















