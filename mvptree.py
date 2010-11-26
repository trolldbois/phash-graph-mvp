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

IMAGE=1
VIDEO=2
AUDIO=4


def distancefunc(pa,pb):
  # pa.hash is a void * pointer.
  # we need to cast it into ulong64* AND get it's value
  d = pHash.ph_hamming_distance(pHash.ulong64Ptr_value(pHash.voidToULong64(pa.hash)), pHash.ulong64Ptr_value(pHash.voidToULong64(pb.hash)))
  return d


class PHashException(BaseException):
  pass

'''
 Object Accessor to MVP functions and structs

 mvp=MVPTree(Dbname) 
 mvp.addFile(filename)
 mvp.addFilesFrom(dirname)
 mvp.query(filename)
 
  
'''
class MVPTree():
  log=None
  db=None
  radius = 30.0
  threshold = 15.0
  knearest = 20
  hashType=None
  callback=None
  mvpfile=None
  #
  __hasher=None
  def __init__(self,dbname,contentType=IMAGE,radius=30.0,threshold=15.0,knearest=20,hashType=pHash.UINT64ARRAY,callback=None):
    self.log=logging.getLogger(self.__class__.__name__)
    self.db=dbname
    self.initContentType(contentType)
    self.radius=radius
    self.threshold=threshold
    self.knearest=knearest
    self.hashType=hashType
    if not callback is None:
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
    return
  '''
  inits hash callbacks and other content dependant fields
  '''
  def initContentType(self,content):
    if content == IMAGE:
      self.__hasher=ImageHasher()
      self.callback=distancefunc
    elif content == VIDEO:
      self.__hasher=VideoHasher()
      self.callback=distancefunc
    elif content == AUDIO:
      self.__hasher=AudioHasher()
      self.callback=distancefunc
    else:
      raise TypeError()
  ############################ ADD   FUNCTIONS #################################  
  '''
    add a single file
  '''
  def addFile(self,filename):
    self.addFiles([filename])
    return
  '''
    add files from directory
  '''
  def addFileFrom(self,dirname):
    # read filenames
    files1=[]
    for root, dirs, files in os.walk(dirname):
      if (root == dirname):
        files1=[os.path.join(root,f) for f in files]
        break
    files1.sort()
    #
    self.addFiles(files1)
    return
  '''
  Add files in args to MVP Databse
  '''
  def addFiles(self,files):
    nbfiles=len(files)
    # make sources struct
    hashlist=pHash.DPptrArray(nbfiles)
    if ( hashlist is None):
      self.log.error("mem alloc error")
      raise MemoryError("mem alloc error")
    # make a datapoint for each file    
    count=0
    tmphash=0x00000000
    for f in files:
      tmpdp=self.makeDatapoint(f)
      tmpdp.thisown=0
      hashlist[count]=tmpdp
      self.log.debug("file[%d] = %s"%( count, f ) )      
      count+=1
    #end for files
    self.log.debug("add %d files to file %s"%(count,self.db))
    nbsaved=0
    # add all files to MVPTree
    ret = pHash.ph_add_mvptree(self.mvpfile, hashlist.cast(), count)
    if (type(ret) is int):
      self.log.error("error on ph_add_mvptree")
      raise PHashException("error on ph_add_mvptree")
    (res,nbsaved)=ret
    self.log.debug("number saved %d out of %d, ret code %d"%( nbsaved,count,res))
    return
 
  ############################ QUERY FUNCTIONS #################################  
  '''
  Query a MVP Tree for files from a directory .
  return a list :
   [ (srcfilename, [ (matcshFilename,score),...] ) , ... ]
  '''
  def queryFilesFrom(self,dirname,ident=None):
    # read filenames
    files1=[]
    for root, dirs, files in os.walk(dirname):
      if (root == dirname):
        files1=[os.path.join(root,f) for f in files]
        break
    files1.sort()
    #
    results=[]
    for f in files1:
      # compute image Hash
      hashp,hashLen=self.__hasher.makeHash(f)
      # put it in datapoint
      # query datapoint
      ret=self.queryHash(hashp,ident=f,hashLen=hashLen)
      results.append((f,ret))
    # return result list
    return results
  '''
  Query for an image file in a MVP Tree.
   @use ph_dct_imagehash
  '''
  def queryFile(self,filename,ident=None):
    if ( not os.access(filename,os.F_OK)):
      raise IOError('file not found: %s'%(filename))
    # compute image Hash
    hashp,hashLen=self.__hasher.makeHash(filename)
    # put it in datapoint
    # query datapoint
    ret=self.queryHash(hashp,ident=filename,hashLen=hashLen)
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
  ############################ UTILS FUNCTIONS #################################  
  def makeDatapoint(self,filename):
    # make datapoint
    tmpdp=pHash.ph_malloc_datapoint(self.mvpfile.hash_type)
    if (tmpdp is None):
      self.log.error("mem alloc error")
      raise MemoryError("mem alloc error")
    # memory ownage
    tmpdp.thisown=0
    # call hasher    
    hashp=0
    hashLen=0
    try:
      hashp,hashLen=self.__hasher.makeHash(filename)
    except PHashException,e:
      self.log.error("unable to get hash: %s"%(filename))
      pHash.ph_free_datapoint(tmpdp)
      raise PHashException("unable to get hash: %s"%(filename))
    # fill DP
    tmpdp.id = filename
    #@TODO that function call is type dependent... voidPtr ?
    tmpdp.hash=pHash.copy_ulong64Ptr(hashp)
    tmpdp.hash_length = 1
    return tmpdp


class Hasher:
  log=None
  def __init__(self):
    self.log=logging.getLogger(self.__class__.__name__)
  '''
    take a filename in input
    return ( hashvalue, haslen )
  '''
  def makeHash(self,filename):
    raise NotImplementedError()


class ImageHasher(Hasher):
  ''' 
  Calls ph_dct_imagehash. hash_lenght is 1  
  '''
  def makeHash(self,filename):
    ret=pHash.ph_dct_imagehash(filename) 
    if (type(ret) is int):
      self.log.error("unable to get hash, retcode %d"%(ret))
      raise PHashException("unable to get hash, retcode %d"%(ret))
    ret2,hashp=ret
    return (hashp,1)
    





def test_addFile1(mvp,dir_name):
  files=None
  for root, dirs, filest in os.walk(dir_name):
    if (root == dir_name):
      files=[os.path.join(root,f) for f in filest]
      break
  files.sort()
  filename=files[0]
  print "add for %s"%( filename)
  # query for image filename
  mvp.addFile(filename)  
  test_queryFile1(mvp,filename)

def test_queryFile1(mvp,filename):
  print "query for %s"%( filename)
  # query for image filename
  res=mvp.queryFile(filename)  
  print " %d files found"%( len(res))
  for match,dist in res:
    print " %s distance = %f"%( match.id, dist)
  return 0



def test_queryFiles2(mvp,dir_name):
  res=mvp.queryFilesFrom(dir_name)  
  for f,matches in res:
    print "query for %s"%( f)
    # query for image filename
    print " %d files found"%( len(matches))
    for match,dist in matches:
      print " %s distance = %f"%( match.id, dist)

  return 0


def test_queryFiles1(mvp,dir_name):
  files=None
  for root, dirs, filest in os.walk(dir_name):
    if (root == dir_name):
      files=[os.path.join(root,f) for f in filest]
      break
  files.sort()
  print "nb query files = %d"%( nbfiles)

  for f in files:
    print "query for %s"%( f)
    # query for image filename
    res=mvp.queryFile(f)  
    print " %d files found"%( len(res))
    for match,dist in res:
      print " %s distance = %f"%( match.id, dist)

  return 0



    
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

  mvp = MVPTree(filename) # IMAGE

  #test_queryFiles1(mvp,dir_name)
  #test_queryFiles2(mvp,dir_name)
  test_addFile1(mvp,dir_name)


if __name__ == '__main__':
  main(sys.argv[1:])

