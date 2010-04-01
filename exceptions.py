class WoWError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return self.msg

class AttachError(WoWError):
	def __init__(self, *args, **kwargs):
		WoWError.__init__(self, *args, **kwargs)

class StateError(WoWError):
	def __init__(self, *args, **kwargs):
		WoWError.__init__(self, *args, **kwargs)

class ObjectManagerError(WoWError):
	def __init__(self, *args, **kwargs):
		WoWError.__init__(self, *args, **kwargs)

class ObjectListError(ObjectManagerError):
	def __init__(self, *args, **kwargs):
		ObjectManagerError.__init__(self, *args, **kwargs)

class ObjectError(WoWError):
	def __init__(self, *args, **kwargs):
		WoWError.__init__(self, *args, **kwargs)

class ObjectInvalidError(ObjectError):
	def __init__(self, *args, **kwargs):
		ObjectError.__init__(self, *args, **kwargs)	

class ObjectAttributeError(ObjectError):
	def __init__(self, *args, **kwargs):
		ObjectError.__init__(self, *args, **kwargs)