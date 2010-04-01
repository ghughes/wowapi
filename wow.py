import sys
from wowapi.defines import constants, fields, offsets
from wowapi.object_manager import ObjectManager
from wowapi.exceptions import *

STATE_NOTATTACHED, STATE_LOGIN, STATE_CHARSELECT, STATE_CHARCREATE, STATE_LOADING, STATE_INGAME = range(0, 6)

def ingame_only(f):
	def wrap(self, *args, **kwargs):
		if self.state == STATE_INGAME:
			return f(self, *args, **kwargs)
		else:
			raise StateError("The game world is not loaded.")
	return wrap

class WoW(object):
	def __init__(self, pid):
		self.offsets = offsets.universal 
		self.offsets.update(fields.fields) # add auto generated field descriptors
		self.constants = constants.constants
		
		if sys.platform == 'darwin':
			self.offsets.update(offsets.mac)
			from mach_vm import VirtualMemory
		else:
			raise EnvironmentError("Your operating system is not supported.")
		
		try:
			self.vm = VirtualMemory(pid)
		except ValueError:
			raise AttachError("Could not attach to the given PID.")
			
		self._objects = ObjectManager(self)
	
	@property
	def attached(self):
		"""Determines whether we're attached to a valid instance of WoW."""
		return True # too lazy to implement this
		
	@property
	def state(self):
		"""Represents the current state of the WoW client."""
		if not self.attached:
			return STATE_NOTATTACHED
		elif self.vm[self.offsets['WORLD_LOADED_STATIC']]:
			return STATE_INGAME
		elif self.vm[self.offsets['WORLD_LOADING_STATIC']]:
			return STATE_LOADING
		elif self.vm.read_string(self.offsets['LOGIN_STATE_STATIC']) == 'charcreate':
			return STATE_CHARCREATE
		elif self.vm.read_string(self.offsets['LOGIN_STATE_STATIC']) == 'charselect':
			return STATE_CHARSELECT
		else:
			return STATE_LOGIN
			
	@property
	@ingame_only
	def objects(self):
		return self._objects
		
	@property
	@ingame_only
	def local_player_guid(self):
		return (self.vm[self.offsets['PLAYER_GUID_STATIC']], self.vm[self.offsets['PLAYER_GUID_STATIC'] + 0x4])
			
def instances():
	#TODO: return list of wow instance PIDs
	pass