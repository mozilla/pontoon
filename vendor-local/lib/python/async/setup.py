#!/usr/bin/env python
from distutils.core import setup, Extension
from distutils.command.build_py import build_py
from distutils.command.build_ext import build_ext

import os, sys

# wow, this is a mixed bag ... I am pretty upset about all of this ... 
setuptools_build_py_module = None
try:
	# don't pull it in if we don't have to
	if 'setuptools' in sys.modules: 
		import setuptools.command.build_py as setuptools_build_py_module
		from setuptools.command.build_ext import build_ext
except ImportError:
	pass

class build_ext_nofail(build_ext):
	"""Doesn't fail when build our optional extensions"""
	def run(self):
		try:
			build_ext.run(self)
		except Exception:
			print "Ignored failure when building extensions, pure python modules will be used instead"
		# END ignore errors

def get_data_files(self):
	"""Can you feel the pain ? So, in python2.5 and python2.4 coming with maya, 
	the line dealing with the ``plen`` has a bug which causes it to truncate too much.
	It is fixed in the system interpreters as they receive patches, and shows how
	bad it is if something doesn't have proper unittests.
	The code here is a plain copy of the python2.6 version which works for all.
	
	Generate list of '(package,src_dir,build_dir,filenames)' tuples"""
	data = []
	if not self.packages:
		return data
		
	# this one is just for the setup tools ! They don't iniitlialize this variable
	# when they should, but do it on demand using this method.Its crazy
	if hasattr(self, 'analyze_manifest'):
		self.analyze_manifest()
	# END handle setuptools ...
	
	for package in self.packages:
		# Locate package source directory
		src_dir = self.get_package_dir(package)

		# Compute package build directory
		build_dir = os.path.join(*([self.build_lib] + package.split('.')))

		# Length of path to strip from found files
		plen = 0
		if src_dir:
			plen = len(src_dir)+1

		# Strip directory from globbed filenames
		filenames = [
			file[plen:] for file in self.find_data_files(package, src_dir)
			]
		data.append((package, src_dir, build_dir, filenames))
	return data
	
build_py.get_data_files = get_data_files
if setuptools_build_py_module:
	setuptools_build_py_module.build_py._get_data_files = get_data_files
# END apply setuptools patch too

    
setup(cmdclass={'build_ext':build_ext_nofail},
      name = "async",
      version = "0.6.1",
      description = "Async Framework",
      author = "Sebastian Thiel",
      author_email = "byronimo@gmail.com",
      url = "http://gitorious.org/git-python/async",
      packages = ('async', 'async.mod', 'async.test', 'async.test.mod'),
      package_data={'async' : ['AUTHORS', 'README']},
      package_dir = {'async':''},
      ext_modules=[Extension('async.mod.zlib', ['mod/zlibmodule.c'])],
      license = "BSD License",
      zip_safe=False,
      long_description = """Async is a framework to process interdependent tasks in a pool of workers"""
      )
