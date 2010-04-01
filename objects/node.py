from wowapi.objects.object import Object, enforce_validity

class Node(Object):
	def __init__(self, *args, **kwargs):
		Object.__init__(self, *args, **kwargs)

	def __repr__(self):
		return "<Node '%s' at %s>" % (self.name, hex(self.base))
		
	@property
	@enforce_validity
	def name(self):
		name_base = self.get_base_int('NODE_NAME_BASE')
		if not name_base:
			return None
			
		name_ptr = self.wow.vm[name_base + self.wow.offsets['NODE_NAME_PTR']]
		name = self.wow.vm.read_string(name_ptr)
		return name if name else None