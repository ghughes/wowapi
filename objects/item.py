from wowapi.objects.object import Object, enforce_validity

class Item(Object):
	def __init__(self, *args, **kwargs):
		Object.__init__(self, *args, **kwargs)

	def __repr__(self):
		return "<Item at %s>" % hex(self.base)