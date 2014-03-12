"""Channel testing"""
from lib import *
from async.util import *
from async.task import *

import time

class TestTask(TestBase):
	
	max_threads = cpu_count()
	
	def test_iterator_task(self):
		# tested via test_pool
		pass
		
