import string
from wowapi.objects.object import Object, enforce_validity
from wowapi.spell import Spell, Aura
from wowapi.position import Position

class Unit(Object):
	def __init__(self, *args, **kwargs):
		Object.__init__(self, *args, **kwargs)
		
	def __repr__(self):
		return "<Unit '%s' at %s>" % (self.name, hex(self.base))
		
	@property
	@enforce_validity
	def position(self):
		return Position(
			x=self.get_base_float('UNIT_XLOCATION'),
			y=self.get_base_float('UNIT_YLOCATION'),
			z=self.get_base_float('UNIT_ZLOCATION')
		)
	
	@property
	def x(self):
		return self.position.x
		
	@property
	def y(self):
		return self.position.y
		
	@property
	def z(self):
		return self.position.z
		
	@property
	@enforce_validity
	def facing(self):
		return (
			self.get_base_float('UNIT_FACING_HORIZONTAL'),
			self.get_base_float('UNIT_FACING_VERTICAL')
		)
		
	@property
	@enforce_validity
	def movement_flags(self):
		return self.get_base_int('UNIT_MOVEMENTFLAGS')
		
	def has_movement_flag(self, flag):
		return bool(self.wow.constants['MOVEMENTFLAG_%s' % string.upper(flag)] & self.movement_flags)
		
	@property
	@enforce_validity
	def speed(self):
		return self.get_base_float('UNIT_RUNSPEED_CURRENT')
		
	@property
	@enforce_validity
	def walk_speed(self):
		return self.get_base_float('UNIT_RUNSPEED_WALK')
		
	@property
	@enforce_validity
	def max_speed(self):
		return self.get_base_float('UNIT_RUNSPEED_MAX')
	
	@property
	@enforce_validity
	def back_speed(self):
		return self.get_base_float('UNIT_RUNSPEED_BACK')
		
	@property
	@enforce_validity
	def max_airspeed(self):
		return self.get_base_float('UNIT_AIRSPEED_MAX')
		
	@property
	@enforce_validity
	def casting(self):
		tocast = self.get_base_int('UNIT_SPELL_TOCAST')
		casting = self.get_base_int('UNIT_SPELL_CASTING')
		target = (
			self.get_base_int('UNIT_SPELL_TARGETGUID_LOW'),
			self.get_base_int('UNIT_SPELL_TARGETGUID_HIGH')
		)
		start = self.get_base_int('UNIT_SPELL_TIMESTART')
		end = self.get_base_int('UNIT_SPELL_TIMEEND')
		
		if tocast or casting:
			return Spell(casting) if casting else Spell(tocast), target, start, end
		else:
			return None, None, None, None
			
	@property
	@enforce_validity
	def channeling(self):
		channeling = self.get_base_int('UNIT_SPELL_CHANNELING')
		start = self.get_base_int('UNIT_SPELL_CHANNELTIMESTART')
		end = self.get_base_int('UNIT_SPELL_CHANNELTIMEEND')
		
		if channeling:
			return Spell(channeling), start, end
		else:
			return None, None, None
			
	@property
	@enforce_validity
	def selection_flags(self):
		return self.get_base_int('UNIT_SELECTIONFLAGS')
		
	@property
	def is_selected(self):
		return bool((1 << 12) & self.selection_flags)
		
	@property
	def is_focused(self):
		return bool((1 << 13) & self.selection_flags)
		
	@property
	@enforce_validity
	def auras(self):
		valid_auras = self.get_base_int('UNIT_AURAS_VALIDCOUNT')
		if valid_auras == 0xFFFFFFFF:
			valid_auras = self.get_base_int('UNIT_AURAS_OVERFLOWVALIDCOUNT')
		if valid_auras <= 0 or valid_auras > 56:
			return [] # not a valid aura count

		auras_base = self.base + self.wow.offsets['UNIT_AURAS_START']
		if valid_auras > 16: # aura overflow
			auras_base = self.base + self.wow.offsets['UNIT_AURAS_OVERFLOWPTR1']
			if not auras_base:
				return [] # error finding aura overflow ptr

		auras = {}
		for i in range(0, valid_auras):
			aura_base = auras_base + (i * 0x18)
			spell_id = self.wow.vm[aura_base + self.wow.offsets['AURA_ENTRYID']]
			if spell_id:
				auras[spell_id] = Aura(
					spell=Spell(spell_id),
					guid=(self.wow.vm[aura_base + self.wow.offsets['AURA_GUID']], self.wow.vm[aura_base + self.wow.offsets['AURA_GUID'] + 0x4]),
					bytes=self.wow.vm[aura_base + self.wow.offsets['AURA_BYTES']],
					duration=self.wow.vm[aura_base + self.wow.offsets['AURA_DURATION']],
					expiration=self.wow.vm[aura_base + self.wow.offsets['AURA_EXPIRATION']]
				)
		return auras

	@property
	@enforce_validity
	def name(self):
		name_base = self.get_base_int('UNIT_NAME_BASE')
		if not name_base:
			return None
			
		name_ptr = self.wow.vm[name_base + self.wow.offsets['UNIT_NAME_PTR']]
		name = self.wow.vm.read_string(name_ptr)
		return name if name else None
		
	@property
	@enforce_validity
	def description(self):
		name_base = self.get_base_int('UNIT_NAME_BASE')
		if not name_base:
			return None
			
		desc_ptr = self.wow.vm[name_base + self.wow.offsets['UNIT_DESC_PTR']]
		desc = self.wow.vm.read_string(desc_ptr)
		return desc if desc else None
		
	@property
	@enforce_validity
	def pet(self):
		guid = self.get_field_guid('UNIT_FIELD_CHARM')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def summon(self):
		guid = self.get_field_guid('UNIT_FIELD_SUMMON')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def charmed_by(self):
		guid = self.get_field_guid('UNIT_FIELD_CHARMEDBY')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def summoned_by(self):
		guid = self.get_field_guid('UNIT_FIELD_SUMMONEDBY')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def created_by(self):
		guid = self.get_field_guid('UNIT_FIELD_CREATEDBY')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def target(self):
		guid = self.get_field_guid('UNIT_FIELD_TARGET')
		if guid and guid in self.wow.objects:
			return self.wow.objects[guid]
		else:
			return None
			
	@property
	@enforce_validity
	def health(self):
		return self.get_field_int('UNIT_FIELD_HEALTH')
			
	@property
	@enforce_validity
	def level(self):
		return self.get_field_int('UNIT_FIELD_LEVEL')
		
	