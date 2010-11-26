# -*- coding: utf-8 -*-


from setuptools import setup
from glob import glob

from distutils.core import setup, Extension

setup(name="phash-graph-mvp",
    version="1.0",
    description="Graph a pHash MVP tree",
    long_description="""
phash-graph-mvp is a small python script which use pHash ( http://www.phash.org/ )
to build a graphical representation of perceptual relation between images.
    """,

    url="http://packages.python.org/phash-graph-mvp/",
    download_url="http://github.com/trolldbois/phash-graph-mvp/tree/master",
    license='GPL',
    classifiers=[
        "Topic :: Multimedia",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GPL",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
    ],
    keywords=['pHash','libphash'],
    author="Loic Jaquemet",
    author_email="loic.jaquemet+python@gmail.com",
    py_modules = ["pHash"], 
#    extras_require = {
#        'CACHE':  ["python-memcached"],
#    },
    #setup_requires=[
    #    "nose",
    #    "sphinx",
    #],
    #test_suite='nose.collector',
)
