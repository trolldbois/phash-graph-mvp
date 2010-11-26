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

# dot graph edito http://tintfu.sourceforge.net/

#

import pHash
from mvptree import MVPTree

import logging,os,re,sys
import networkx as nx
import time, locale

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pygraphviz as pgv

'''
find relation between files in a MVP Database

We use networkx to be able to play with graph algorithms
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
    self.__dirname=dirname
    myfiles=None
    for root,dirs,files in os.walk(dirname):
      if (root==dirname):
        # make all nodes
        for f in files:
          self.log.debug(" Adding node %s"%(f))
          self.graph.add_node(f)
        myfiles=[os.path.join(root,fname) for fname in files]
    self.log.info("Found %d files in %s"%(len(myfiles),dirname) )
    # query edges  
    self.log.info("Querying %d files in MVPTree %s"%(len(myfiles),self.tree.db) )
    queryResults=self.tree.queryFiles(myfiles)
    # add edges
    for srcfile,matches in queryResults:
      for match,dist in matches:
        #self.log.debug("match : %s , %f"%(match.id,dist))
        tget=os.path.basename(match.id)
        #self.log.debug(" tget node : %s"%(tget))
        if tget not in self.graph:
          self.log.warning(" Adding tget node ... weird ... : %s "%(match.id))
          self.graph.add_node(tget)
        # add edge
        sfile=os.path.basename(srcfile)
        if ( sfile != tget ):
          self.log.debug("ADDING EDGE : %s -- %s"%(sfile,tget))
          self.graph.add_edge(sfile,tget,{'weight':dist})
    # graph is done
    self.log.info("Build %d nodes and %d edges"%(len(self.graph.nodes()),len(self.graph.edges())))
    return
  #      if (len(self.graph.neighbors(dom))>20):
  #        # ignore , yen a trop
  #          self.graph.add_edge(dom,spamurl.url.hostname,{'weight':1})
  def makeGraph(self,filename,graph=None,w=12,h=8):
    if (graph is None):
      graph=self.graph
    outdot=filename+'.dot'
    self.log.info('Creating graph Image: %s , dotfile: %s '%(filename,outdot))
    # WTF... INCHES !
    self.log.debug('making graph')
    G=nx.to_agraph(graph)
    
    self.log.debug('%d nodes'%(len( G.nodes()) ) )
    
    G.graph_attr['label']='Graph %s'%(self.tree.db)
    #G.graph_attr['labelfontsize']='400'
    G.graph_attr['overlap']='no'

    G.node_attr['shape']='none'
    G.node_attr['imagescale']='true'
    G.node_attr['fixedsize']='true'
    for n in G.nodes():
      n.attr['image']=os.path.join(self.__dirname,n)
      n.attr['label']=n
      #n.attr['labelfontsize']='60'
      #n.attr['width']='3'
    
    
    G.edge_attr['color']='red'
    #G.edge_attr['len']='1'
    
    
    G.layout(prog="neato")
    self.log.debug('drawing %s '%(filename))
    G.draw(filename)
    self.log.debug('writing  %s '%(outdot))
    G.write(outdot)
    return G



def main(argv):
  '''
  '''
  #locale.setlocale(locale.LC_ALL,'fr_FR')
  logging.basicConfig(level=logging.INFO)

  if len(argv) <3 :
    logging.error('usage: graphmvp.py <dirname> <dbname> <outputgraph>') 
    return 
  
  dirname=argv[0]
  db=argv[1]
  outputfile=argv[2]
  
  g= MVPGraph(db)
  g.build(dirname)
  g.makeGraph(outputfile)



if __name__ == '__main__':
  main(sys.argv[1:])
















