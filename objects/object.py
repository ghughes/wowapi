from wowapi.exceptions import ObjectInvalidError

TYPE_UNKNOWN, TYPE_ITEM, TYPE_CONTAINER, TYPE_UNIT, TYPE_PLAYER, TYPE_GAMEOBJECT, TYPE_DYNAMICOBJECT, \
	TYPE_CORPSE, TYPE_AIGROUP, TYPE_AREATRIGGER = range(0, 10)
	
def enforce_validity(f):
	def wrap(self, *args, **kwargs):
		if self.valid:
			return f(self, *args, **kwargs)
		else:
			raise ObjectInvalidError("Referenced object is no longer available in memory.")
	return wrap

class Object(object):
	def __init__(self, base, wow):
		self.base = base
		self.wow = wow
		self.stale = False
		self._guid = self.get_base_guid('OBJECT_GUID_ALL64')
	
	def __repr__(self):
		return "<Object %s at %s>" % (self.guid, hex(self.base))
		
	def get_base_int(self, name):	
		return self.wow.vm[self.base + self.wow.offsets[name]]
		
	def get_base_float(self, name):
		return self.wow.vm.read_float(self.base + self.wow.offsets[name])
		
	def get_base_guid(self, name):
		guid = (self.wow.vm.read_int(self.base + self.wow.offsets[name]), self.wow.vm.read_int(self.base + self.wow.offsets[name] + 0x4))
		return guid if guid != (0, 0) else None
		
	def get_field_int(self, name):
		return self.wow.vm[self.fields_ptr + self.wow.offsets[name]]
		
	def get_field_float(self, name):
		return self.wow.vm.read_float(self.fields_ptr + self.wow.offsets[name])
		
	def get_field_guid(self, name):
		guid = (self.wow.vm.read_int(self.fields_ptr + self.wow.offsets[name]), self.wow.vm.read_int(self.fields_ptr + self.wow.offsets[name] + 0x4))
		return guid if guid != (0, 0) else None
			
	@property
	def valid(self):
		if self.stale: # guid *definitely* isn't in object list anymore
			return False
		
		t = self.get_base_int('OBJECT_TYPE_ID')
		guid = self.get_base_guid('OBJECT_GUID_ALL64')
		
		if not t or t <= self.wow.constants['TYPE_UNKNOWN'] or t >= self.wow.constants['TYPE_MAX'] or guid != self._guid:
			if self._guid in self.wow.objects: # object has moved - get new base from object manager
				self.base = self.wow.objects[self._guid].base
			else:
				return False # object is completely gone

		return True
			
	@property
	@enforce_validity
	def base_id(self):
		return self.get_base_int('OBJECT_BASE_ID')
		
	@property
	@enforce_validity
	def fields_ptr(self):
		return self.get_base_int('OBJECT_FIELDS_PTR')
		
	@property
	@enforce_validity
	def object_type(self):
		t = self.get_base_int('OBJECT_TYPE_ID')
		
		if t == self.wow.constants['TYPE_ITEM']:
			return TYPE_ITEM
		elif t == self.wow.constants['TYPE_CONTAINER']:
			return TYPE_CONTAINER
		elif t == self.wow.constants['TYPE_UNIT']:
			return TYPE_UNIT
		elif t == self.wow.constants['TYPE_PLAYER']:
			return TYPE_PLAYER
		elif t == self.wow.constants['TYPE_GAMEOBJECT']:
			return TYPE_GAMEOBJECT
		elif t == self.wow.constants['TYPE_DYNAMICOBJECT']:
			return TYPE_DYNAMICOBJECT
		elif t == self.wow.constants['TYPE_CORPSE']:
			return TYPE_CORPSE
		elif t == self.wow.constants['TYPE_AIGROUP']:
			return TYPE_AIGROUP
		elif t == self.wow.constants['TYPE_AREATRIGGER']:
			return TYPE_AREATRIGGER
		else:
			return TYPE_UNKNOWN
			
	@property
	@enforce_validity
	def guid(self):
		return self._guid # never changes, so use cached value
	
	@property
	@enforce_validity
	def scale(self):
		return self.get_field_float('OBJECT_FIELD_SCALE_X')
