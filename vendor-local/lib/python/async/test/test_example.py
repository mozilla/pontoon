"""Module containing examples from the documentaiton"""
from lib import *

from async.pool import *
from async.task import *
from async.thread import terminate_threads




class TestExamples(TestBase):
	
	@terminate_threads
	def test_usage(self):
		p = ThreadPool()
		# default size is 0, synchronous mode
		assert p.size() == 0
		
		# now tasks would be processed asynchronously
		p.set_size(1)
		assert p.size() == 1
		
		# A task performing processing on items from an iterator
		t = IteratorThreadTask(iter(range(10)), "power", lambda i: i*i)
		reader = p.add_task(t)
		
		# read all items - they where procesed by worker 1
		items = reader.read()
		assert len(items) == 10 and items[0] == 0 and items[-1] == 81
		
		
		# chaining 
		t = IteratorThreadTask(iter(range(10)), "power", lambda i: i*i)
		reader = p.add_task(t)
		
		# chain both by linking their readers
		tmult = ChannelThreadTask(reader, "mult", lambda i: i*2)
		result_reader = p.add_task(tmult)
		
		# read all
		items = result_reader.read()
		assert len(items) == 10 and items[0] == 0 and items[-1] == 162
		
		
