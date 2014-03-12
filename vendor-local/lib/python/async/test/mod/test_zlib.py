"""ZLib module testing"""
from async.test.lib import *
import async.mod.zlib as zlib

import sys
import struct

class TestZLib(TestBase):
	def test_constants(self):
		# check constants
		assert zlib.Z_STATUS_UNSET == ~0
		assert hasattr(zlib, "Z_OK")
		assert hasattr(zlib, "Z_STREAM_END")
		assert hasattr(zlib, "Z_NEED_DICT")
		assert hasattr(zlib, "Z_ERRNO")
		assert hasattr(zlib, "Z_STREAM_ERROR")
		assert hasattr(zlib, "Z_DATA_ERROR")
		assert hasattr(zlib, "Z_MEM_ERROR")
		assert hasattr(zlib, "Z_BUF_ERROR")
		assert hasattr(zlib, "Z_VERSION_ERROR")
		
		
	def test_status(self):
		# test the newly introduced status code
		data = struct.pack(">L", (1<<31) + (1<<15) + (1<<2))
		assert len(data) == 4
		
		# compress
		cobj = zlib.compressobj(zlib.Z_BEST_SPEED)
		assert cobj.status == zlib.Z_STATUS_UNSET
		
		cchunk = ''
		for c in data:
			cchunk += cobj.compress(c)
			assert cobj.status == zlib.Z_OK
		# END for each databyte
		# its not yet done, but soon it will
		cchunk += cobj.flush()
		assert cobj.status == zlib.Z_STREAM_END
		
		# zip should have added a few bytes of info
		assert len(cchunk) > len(data)
		
		
		# decompress - need status to determine decompession finished
		dcobj = zlib.decompressobj()
		idata = ''						# inflated data
		for i, c in enumerate(cchunk):
			idata += dcobj.decompress(c)
			assert dcobj.status == zlib.Z_OK
			
			# break if we have it
			if len(idata) == len(data):
				break
		# END for each character
		assert idata == data
		
		# we should still have some bytes left
		assert i < len(cchunk) - 1
		
		# feed the remaining data, we don't expect to decompress anything, but
		# want to see the status change
		while dcobj.status == zlib.Z_OK:
			i += 1
			assert len(dcobj.decompress(cchunk[i])) == 0
		# END deplete compressed stream
		
		# now we are done
		assert dcobj.status == zlib.Z_STREAM_END
		assert i == len(cchunk) - 1
