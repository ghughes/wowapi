class Spell(object):
	def __init__(self, id):
		self.id = id
		self.name = "Unknown"
		
	def __str__(self):
		return "<Spell: ''>"

class Aura(object):
	def __init__(self, spell, guid, bytes, duration, expiration):
		self.spell = spell
		self.guid = guid
		self.bytes = bytes
		self.duration = duration
		self.expiration = expiration
		
	def __str__(self):
		return "<Aura: '%s' affecting GUID %s>" % (self.spell.name, repr(self.guid))

	@property
	def stacks(self):
		return ((self.bytes >> 16) & 0xFF)
	
	@property
	def level(self):
		return ((self.bytes >> 8) & 0xFF)
	
	@property
	def is_debuff(self):
		return bool((self.bytes >> 7) & 1)
	
	@property
	def is_active(self):
		return bool((self.bytes >> 5) & 1)
	
	@property
	def is_passive(self):
		return bool((self.bytes >> 4) & 1) and not self.is_active
	