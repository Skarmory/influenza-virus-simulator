from distutils.core import setup
import py2exe
#import glob

import numpy
import matplotlib
#matplotlib.use('wxagg') # overrule configuration
import random

 
py2exe_options={"py2exe":{
							"includes":["matplotlib.backends.backend_tkagg"], 
							"dll_excludes": ['MSVCP90.dll'],
							#'excludes': ['_gtkagg', '_tkagg'],
						  }
				}
						  
setup(
		data_files=matplotlib.get_py2exe_datafiles(), 
		options=py2exe_options,
		console=['test.py'])