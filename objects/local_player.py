from wowapi.objects.object import Object, enforce_validity
from wowapi.objects.player import Player

class LocalPlayer(Player):
	def __init__(self, *args, **kwargs):
		Player.__init__(self, *args, **kwargs)
		
	def __repr__(self):
		return "<LocalPlayer '%s' at %s>" % (self.name, hex(self.base))
		
	@property
	@enforce_validity
	def critter(self):
	 	guid = self.get_field_guid('UNIT_FIELD_CRITTER')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None

	@property
	@enforce_validity
	def xp(self):
		return self.get_field_int('PLAYER_XP')

	@property
	@enforce_validity
	def next_level_xp(self):
		return self.get_field_int('PLAYER_NEXT_LEVEL_XP')

	@property
	@enforce_validity
	def money(self):
		return self.get_field_int('PLAYER_FIELD_COINAGE')
	