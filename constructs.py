class LinkedList(object):
	"""Represents a linked list in WoW's memory."""
	def __init__(self, base, wow):
		self.base = base
		self.wow = wow
	
	def __iter__(self):
		base = self.base
		stack = []
		
		while self.wow.vm[base] == 0x4:
			ptr1 = self.wow.vm[base + 0x4] - 0x4
			ptr2 = self.wow.vm[base + 0x8]

			if ptr1 - base != 0x4:
				yield ptr1
				stack.append(ptr1)
				
			if ptr2 - base != 0x5:
				yield ptr2
				
			base += 0xC

		while len(stack) > 0:
			ptr = stack.pop()
			next = self.wow.vm[ptr + 0x4] - 0x4
			
			if self.wow.vm[next] != 0x4:
				yield next
				stack.append(next)
		
	def __len__(self):
		count = 0
		for i in self:
			count += 1
		return count

	def __getitem__(self, item):
		for i in self:
			if self.wow.vm[i] == item:
				return i
		return None
	