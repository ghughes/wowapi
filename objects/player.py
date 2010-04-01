from wowapi.objects.object import Object, enforce_validity
from wowapi.objects.unit import Unit
from wowapi.constructs import LinkedList

class Player(Unit):
	def __init__(self, *args, **kwargs):
		Unit.__init__(self, *args, **kwargs)
		
	def __repr__(self):
		return "<Player '%s' at %s>" % (self.name, hex(self.base))
	
	@property
	@enforce_validity
	def name(self):
		for base in LinkedList(self.wow.vm[self.wow.offsets['PLAYER_NAMES_LL_PTR']], self.wow):
			if (self.wow.vm[base + 0x14], self.wow.vm[base + 0x18]) == self.guid:
				return self.wow.vm.read_string(base + 0x1C)
		return None
	
	@property
	@enforce_validity
	def guild_id(self):
		return self.get_field_int('PLAYER_GUILDID')
	
	@property
	@enforce_validity
	def guild(self):
		if not self.guild_id:
			return None
		
		for base in LinkedList(self.wow.vm[self.wow.offsets['GUILD_NAMES_LL_PTR']], self.wow):
			if self.wow.vm[base + 0x14] == self.guild_id:
				return self.wow.vm.read_string(base + 0x18)
		return None
	
	@property
	def description(self):
		return self.guild_name
	