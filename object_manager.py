import logging
from datetime import datetime, timedelta
from wowapi.objects import Item, LocalPlayer, Node, Object, Player, Unit
from wowapi.exceptions import ObjectManagerError, ObjectListError

EXPIRES_AFTER = timedelta(seconds=2)

def refresh_object_cache(f):
	def wrap(self, *args, **kwargs):
		if not self.last_update or datetime.now() >= (self.last_update + EXPIRES_AFTER):
			self.update()
		return f(self, *args, **kwargs)
	return wrap

class ObjectManager:
	def __init__(self, wow):
		self.wow = wow
		self.objects = {}
		self.list_ptr = None
		self.last_update = None
		self.local_player_guid = None

	@property
	def player(self):
		"""Shortcut to local player."""
		guid = self.local_player_guid
		if not guid: # not cached yet?
			guid = self.wow.local_player_guid
			
		if not guid:
			raise ObjectManagerError("Could not read player GUID.")
		elif guid in self:
			return self[guid]
		else:
			raise ObjectListError("Player not present in object list.")
			
	@property
	def target(self):
		"""Shortcut to local player's target."""
		return self.player.target
			
	@refresh_object_cache
	def __getitem__(self, item):
		return self.objects[item]
	
	@refresh_object_cache		
	def __contains__(self, key):
		return key in self.objects
	
	@refresh_object_cache
	def __iter__(self):
		for guid, obj in self.objects.items():
			yield obj
			
	@refresh_object_cache
	def __len__(self):
		return len(self.objects)
		
	def _locate_base(self):
		"""Finds the top of WoW's object list within dynamic memory."""
		self.list_ptr = None
		start = 0
		
		while self.list_ptr is None and start < 0xFFFFFFFF:
			ptr1 = self.wow.vm[self.wow.offsets['OBJECT_LIST_LL_PTR']]
			
			if not ptr1:
				logging.getLogger(self.__class__.__name__).warning("Falling back to depth search for object list")
				ptr1 = self.wow.vm.search('\x88\xae\xbf\x00', start, 'MALLOC_TINY')
			
			if ptr1:
				ptr2 = self.wow.vm[ptr1 + 0x1C]
				
				if ptr2 is not None:
					if self.wow.vm[ptr2] == 0x18: # object list head
						logging.getLogger(self.__class__.__name__).debug("Located object list at %s" % hex(ptr2))
						self.list_ptr = ptr2
						return True
			else:
				break # search failed
						
			start = ptr1 + 0x4
				
		return False
	
	def update(self):
		"""Scans WoW's object list and caches the results internally."""
		for obj in self.objects.values():
			obj.stale = True
	
		if self.list_ptr is None or self.wow.vm[self.list_ptr] != 0x18: # don't have valid pointer
			if not self._locate_base():
				raise ObjectListError("Failed to locate object list in memory.")
				
		self.local_player_guid = self.wow.local_player_guid # cache this for speed	
			
		base = self.list_ptr
		explored = []
		stack = []
	
		while self.wow.vm[base] == 0x18:
			ptr1 = self.wow.vm[base + 0x4]
			ptr2 = self.wow.vm[base + 0x8]
		
			if ptr1 != base + 0x4:
				self.load(ptr1 - 0x18)
			if ptr2 != base + 0x5:
				self.load(ptr2)			

			stack.append(ptr1 - 0x18)	
			base += 0xC

		while len(stack) > 0:
			ptr = stack.pop()

			if ptr in explored:
				continue
			else:
				explored.append(ptr)
	
			next = self.wow.vm[ptr + self.wow.offsets['OBJECT_STRUCT4_POINTER']]
			if next > 0:
				self.load(next)
				stack.append(next)
			
		for k, v in self.objects.items():
			if v.stale:
				del self.objects[k] # prune stale objects
		
		if len(self.objects) > 0:
			self.last_update = datetime.now()
			return True
		else:
			raise ObjectListError("Object list contains zero objects.")
		
	def load(self, base):
		"""Loads an object into the local cache."""
		try:
			obj_type = self.wow.vm[base + self.wow.offsets['OBJECT_TYPE_ID']]
		except:
			return False # invalid
		
		if obj_type <= self.wow.constants['TYPE_UNKNOWN'] or obj_type >= self.wow.constants['TYPE_MAX']:
			return False # invalid
		
		guid = (self.wow.vm[base + self.wow.offsets['OBJECT_GUID_ALL64']], self.wow.vm[base + self.wow.offsets['OBJECT_GUID_ALL64'] + 0x4])
		
		if guid in self.objects:
			self.objects[guid].stale = False
		elif obj_type == self.wow.constants['TYPE_ITEM']:
			self.objects[guid] = Item(base, self.wow)
		elif obj_type == self.wow.constants['TYPE_UNIT']:
			self.objects[guid] = Unit(base, self.wow)
		elif obj_type == self.wow.constants['TYPE_PLAYER'] and guid == self.local_player_guid:
			self.objects[guid] = LocalPlayer(base, self.wow)
		elif obj_type == self.wow.constants['TYPE_PLAYER']:
			self.objects[guid] = Player(base, self.wow)
		elif obj_type == self.wow.constants['TYPE_GAMEOBJECT']:
			self.objects[guid] = Node(base, self.wow)
			
		return True
