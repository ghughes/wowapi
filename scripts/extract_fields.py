# Based on http://code.google.com/p/mywowtools/source/browse/trunk/extractors/uf_extractor/uf_extractor/Program.cs?r=121
import sys, string, struct, datetime

field_flags = {
	'NONE':			0,
	'PUBLIC':		1,
	'PRIVATE':		2,
	'OWNER_ONLY':	4,
	'UNK1':			8,
	'UNK2':			16,
	'UNK3':			32,
	'GROUP_ONLY':	64,
	'UNK4':			128,
	'DYNAMIC':		256,
}
field_types = ['NONE', 'INT', 'TWO_SHORT', 'FLOAT', 'GUID', 'BYTES']

def main(*argv):
	if len(argv) < 2:
		print "The absolute path to WoW.exe must be given as the only argument to this script."
		return

	f = open(argv[1], 'rb')
	str_data = f.read() # read entire binary as a string
	names_start = string.index(str_data, "OBJECT_FIELD_GUID" + chr(0))
	info_start = string.index(str_data, chr(0)*4 + chr(2) + chr(0)*3 + chr(4) + chr(0)*3 + chr(1) + chr(0)*3) - 4
	f.seek(info_start)
	names_delta = struct.unpack('I', f.read(4))[0] - names_start
	f.seek(info_start)
	
	fields = {}
	
	while True:	
		p1 = struct.unpack('I', f.read(4))[0]
		if p1 < 0x9999:
			p1 = struct.unpack('I', f.read(4))[0]
		p2, p3, p4, p5 = struct.unpack('IIII', f.read(16))
		
		old_pos = f.tell()
		f.seek(p1 - names_delta)
		name = read_str(f)
		f.seek(old_pos)
		
		if p5 > 0:
			flags = []
			for k, v in field_flags.items():
				if p5 & v:
					flags.append(k)
			flags = ', '.join(flags)
		else:
			flags = "NONE"
			
		if p4 < len(field_types):
			ftype = field_types[p4]
		else:
			ftype = "NONE"
			
		group = name.partition("_")[0] if name != "OBJECT_FIELD_CREATED_BY" else "GAMEOBJECT"
		if group not in fields:
			fields[group] = []

		fields[group].append([name, p2 * 4, p3, ftype, flags])
		
		if name == "CORPSE_FIELD_PAD":
			break
			
	for group, f in fields.items():
		last_field = f[len(f) - 1]
		if last_field[3] == "GUID":
			f.append([group + '_END', last_field[1] + 8])
		else:
			f.append([group + '_END', last_field[1] + 4])
			
	print "# Auto generated at %s" % datetime.datetime.now().isoformat()
	print "fields = {"
	output_fields(fields, "OBJECT")
	output_fields(fields, "ITEM", "OBJECT")
	output_fields(fields, "CONTAINER", "ITEM")
	output_fields(fields, "UNIT", "OBJECT")
	output_fields(fields, "PLAYER", "UNIT")
	output_fields(fields, "GAMEOBJECT", "OBJECT")
	output_fields(fields, "DYNAMICOBJECT", "OBJECT")
	output_fields(fields, "CORPSE", "OBJECT")
	print "}"

def output_fields(fields, group, parent=None):
	if parent:
		base = fields[parent][len(fields[parent]) - 1][1]
	else:
		base = 0
	
	for field in fields[group]:
		field[1] = base + field[1]
		print "\t'%s':\t%s," % (field[0], hex(field[1])),
		
		if field[0] != group + "_END":
			print "# Size: %d, Type: %s, Flags: %s" % (field[2] * 4, field[3], field[4])
		
	print

def read_str(f):
	temp = ''
	while True:
		s = f.read(1)
		if not s or s == '\x00':
			break
		else:
			temp += s
	return temp.strip()

if __name__ == '__main__':
    main(*sys.argv)