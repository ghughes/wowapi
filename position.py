class Position(object):
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z
		
	def __repr__(self):
		return "<Position x=%f y=%f z=%f>" % (self.x, self.y, self.z)