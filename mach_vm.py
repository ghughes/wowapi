import os, sys, re
from ctypes import *
from ctypes.util import find_library

class VM_REGION_BASIC_INFO(Structure):
	_fields_ = [("protection", c_int),
	            ("max_protection", c_int),
	            ("inheritance", c_uint),
				("shared", c_int),
				("reserved", c_int),
				("offset", c_uint),
				("behavior", c_int),
				("user_wired_count", c_ushort)]

class VirtualMemory(object):
	def __init__(self, pid):
		if sys.platform != 'darwin':
			raise EnvironmentError("Platform not supported.")
		elif os.getuid() != 0:
			raise EnvironmentError("Not running as root.")
		
		self.pid = pid
		self.libSystem = CDLL(find_library("System"))
		self.seek_address = 0
		
		t = c_uint()
		if self.libSystem.task_for_pid(self.libSystem.mach_task_self(), pid, byref(t)) > 0:
			raise ValueError("task_for_pid() failed - invalid PID?")
		else:
			self.task = t.value # having this makes the target process our bitch
	
	def _read(self, address, buf):
		count = c_uint(sizeof(type(buf)))
		result = self.libSystem.vm_read_overwrite(self.task, address, count, byref(buf), byref(count))

		if result > 0:
			return None # couldn't read given memory block
		else:
			return buf
	
	def read_string(self, address):
		s = ""
		i = 0
		bufsize = 32
		while len(s) < 4096: # max 4kb
			tmp = self._read(address + i, create_string_buffer(bufsize))
			nul = tmp.raw.find('\x00')
			if nul > -1:
				s += tmp.value[:nul]
				return s # if nul char encountered
			else:
				s += tmp.value
				i += bufsize
		return s # if reached size limit
		
	def read_int(self, address):
	 	v = self._read(address, c_int())
		if v is not None:
			return v.value
		else:
			return None

	def read_float(self, address):
	 	v = self._read(address, c_float())
		if v is not None:
			return v.value
		else:
			return None
			
	def read(self, size):
		return self._read(self.seek_address, create_string_buffer(size))
		self.seek_address += size
		
	def seek(self, address):
		self.seek_address = address
		
	def tell(self):
		return self.seek_address
		
	def write_var(self, address, data):
		if isinstance(data, str) and len(data) == 1: # char
			buf = c_char(data)
		elif isinstance(data, str): # string
			buf = create_string_buffer(data)
		elif isinstance(data, int): # int
			buf = c_int(data)
		elif isinstance(data, float): # float
			buf = c_float(data)		
			
		if self.libSystem.vm_write(self.task, address, byref(buf), sizeof(type(buf))) > 0:
			raise ValueError("Error writing to given memory address.")
		else:
			return True
			
	def write(self, text):
		self.write_var(self.seek_address, str(text))
		self.seek_address += len(str(text))
	
	def search(self, regex, start=0, region=''):
		"""Fast pattern search using vmmap.""" # nasty but it works (vmmap uses a private framework anyway)
		result = os.popen("vmmap %d | grep \"%s\"" % (self.pid, region)).readlines()
		vmmap_re = re.compile("^(.+)\s+([a-z0-9]{8})-([a-z0-9]{8})\s+\[")
		scan_re = re.compile(regex, re.DOTALL)
		
		for line in result:
			m = vmmap_re.match(line)
			if not m:
				continue
			
			address = c_uint(int(m.group(2), 16))
			size = c_uint(int(m.group(3), 16) - address.value)
			buf = create_string_buffer(size.value)
			count = c_uint(size.value)
			
			if start > address.value + size.value:
				continue
			
			if self.libSystem.vm_read_overwrite(self.task, address, size, byref(buf), byref(count)) == 0:
				offset = start - address.value if start - address.value > 0 else 0
				m = scan_re.search(buf.raw[offset:])
				if m:
					return long(address.value + m.start() + offset)	
		
		return False
	
	def __getitem__(self, key):
		if isinstance(key, slice):
			if key.start is None:
				return self._read(0x0, create_string_buffer(key.stop))
			elif key.stop is None:
				return self._read(key.start, create_string_buffer(0xffffffff - key.start))
			else:
				return self._read(key.start, create_string_buffer(key.stop - key.start))
		elif (isinstance(key, int) or isinstance(key, long)) and key >= 0x0 and key <= 0xffffffff:
			return self.read_int(key)
		else:
			raise KeyError("Key must be a valid slice or memory address.")
		
	def __setitem__(self, key, value):
		if (isinstance(key, int) or isinstance(key, long)) and key >= 0x0 and key <= 0xffffffff:
			self.write(key, value)
		else:
			raise KeyError("Key must be a valid memory address.")
