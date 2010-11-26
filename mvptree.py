#!/usr/bin/python -OO
# -*- coding: iso-8859-15 -*-
#
#
#    pHash, the open source perceptual hash library
#    Copyright (C) 2009 Aetilius, Inc.
#    All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Loic Jaquemet - loic.jaquemet+swig@gmail.com
#

import pHash
import locale,logging,os,sys,time
from os.path import join


def distancefunc(pa,pb):
  # pa.hash is a void * pointer.
  # we need to cast it into ulong64* AND get it's value
  d = pHash.ph_hamming_distance(pHash.ulong64Ptr_value(pHash.voidToULong64(pa.hash)), pHash.ulong64Ptr_value(pHash.voidToULong64(pb.hash)))
  return d


class MVPTree():
  log=None
  db=None
  radius = 30.0
  threshold = 15.0
  knearest = 20
  hashType=None
  callback=None
  mvpfile=None
  def __init__(self,dbname,radius=30.0,threshold=15.0,knearest=20,hashType=pHash.UINT64ARRAY,callback=distancefunc):
    self.log=logging.getLogger(self.__class__.__name__)
    self.db=dbname
    self.radius=radius
    self.threshold=threshold
    self.knearest=knearest
    self.hashType=hashType
    self.callback=callback
    self.initMVPFile()
  '''
  Init the MVPFile struct
  '''
  def initMVPFile(self):
    self.mvpfile=None
    self.mvpfile=pHash.MVPFile()
    self.mvpfile.filename = self.db
    pHash.my_set_callback(self.mvpfile,self.callback)  
    self.mvpfile.hash_type = self.hashType

  '''
  Query for an image file in a MVP Tree.
   @use ph_dct_imagehash
  '''
  def queryImage(self,filename,ident=None):
    if ( not os.access(filename,os.F_OK)):
      raise IOError('file not found: %s'%(filename))
    # compute image Hash
    hashp=self.makeImageHash(filename)
    # put it in datapoint
    # query datapoint
    ret=self.queryHash(hashp,ident=filename,hashLen=1)
    # return result list
    return ret
  '''
  Query for an hash in a MVP Tree.
   @use ph_dct_imagehash
  '''
  def queryHash(self,hashp,ident="unknownId",hashLen=1):
    # put it in datapoint
    #DP *query = pHash.ph_malloc_datapoint(mvpfile.hash_type)
    #query=pHash.ph_malloc_datapoint(mvpfile.hash_type)
    query=pHash.DP()
    if (query is None):
      self.log.error("mem alloc error")
      raise PHashException("mem alloc error")
    # memory ownage ...== 1
    #print '    query.thisown ',    query.thisown
    #query.thisown=0
    # fill fields 
    query.id = ident
    query.hash = pHash.copy_ulong64Ptr(hashp)
    query.hash_length = hashLen
    # query datapoint    
    return self.query(query)
  '''
    Query a datapoint 
    
    return a list of tuple results
      [ ( dpmatch, distance),..]
  '''    
  def query(self,datapoint,callback=distancefunc):
    if not type(datapoint) is pHash.DP:
      raise TypeError("expected a pHash.DP instance")
    # refresh info....
    self.initMVPFile()
    # malloc results structure 
    results = pHash.DPptrArray(self.knearest)
    # error handling
    if (results is None):
      raise MemoryError("expected a pHash.DP instance")
      
    # query datapoint in MVP tree
    ret = pHash.ph_query_mvptree(self.mvpfile,datapoint,self.knearest,self.radius,self.threshold,results.cast())
    # error handling
    if (type(ret) is int ):
      self.log.error("could not complete query, %d"%(retcode))
      raise PHashException("could not complete query, %d"%(retcode))
    retcode,nbfound = ret
    if (retcode != pHash.PH_SUCCESS and retcode != pHash.PH_ERRCAP):
      self.log.error("could not complete query, %d"%(retcode))
      raise PHashException("could not complete query, %d"%(retcode))

    # results treatment
    self.log.debug(" %d files found"%( nbfound))
    #
    for j in range (0,nbfound):
      # this own == false
      #print 'thisown',results[j].thisown
      #results[j].thisown=1
      # free dp.id ? 
      # free dp.hash ?
      pass
    res=[ (results[j],distancefunc(datapoint, results[j]) ) for j in range (0,nbfound)]
    return res
  ''' 
  Calls ph_dct_imagehash. hash_lenght is 1
  '''
  def makeImageHash(self,filename):
    ret=pHash.ph_dct_imagehash(filename) 
    if (type(ret) is int):
      self.log.error("unable to get hash, retcode %d"%(ret))
      raise PHashException("unable to get hash, retcode %d"%(ret))
    ret2,hashp=ret
    return hashp
    
    
def main(argv):
  '''
  '''
  logging.basicConfig(level=logging.DEBUG)
  
  print pHash.ph_about()

  if (len(argv) < 2):
    print "not enough input arguments"
    print "usage: %s directory dbname [radius] [knearest] [threshold]"%( sys.argv[0])
    return -1

  dir_name = argv[0]#/* name of files in directory of query images */
  filename = argv[1]#/* name of file to save db */

  print "using db %s"%( filename)
  print "using dir %s for query files"%( dir_name)

  mvp = MVPTree(filename)
  
  nbfiles=0
  files=None
  for root, dirs, filest in os.walk(dir_name):
    nbfiles=len(filest)
    files=[os.path.join(root,f) for f in filest]
  files.sort()
  print "nb query files = %d"%( nbfiles)

  for f in files:
    print "query for %s"%( f)
    # query for image filename
    res=mvp.queryImage(f)  
    print " %d files found"%( len(res))
    for match,dist in res:
      print " %s distance = %f"%( match.id, dist)

  return 0


if __name__ == '__main__':
  main(sys.argv[1:])

