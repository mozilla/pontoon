"""Initialize the multi-processing package"""

#{ Initialization
def _init_atexit():
	"""Setup an at-exit job to be sure our workers are shutdown correctly before
	the interpreter quits"""
	import atexit
	import thread
	atexit.register(thread.do_terminate_threads)
	
def _init_signals():
	"""Assure we shutdown our threads correctly when being interrupted"""
	import signal
	import thread
	import sys
	
	prev_handler = signal.getsignal(signal.SIGINT)
	def thread_interrupt_handler(signum, frame):
		thread.do_terminate_threads()
		if callable(prev_handler):
			prev_handler(signum, frame)
			raise KeyboardInterrupt()
		# END call previous handler
	# END signal handler
	try:
		signal.signal(signal.SIGINT, thread_interrupt_handler)
	except ValueError:
		# happens if we don't try it from the main thread
		print >> sys.stderr, "Failed to setup thread-interrupt handler. This is usually not critical"
	# END exception handling


#} END init

_init_atexit()
_init_signals()


# initial imports
from task import *
from pool import *
from channel import *
