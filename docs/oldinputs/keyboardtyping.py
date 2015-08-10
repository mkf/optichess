# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.look.eye import eye,shot
class keyboardtyping(eye):
	def __init__(self): pass
	def __enter__(self):
		print "Hej"
		return self
	def __exit__(self, exc_type, exc_val, exc_tb):
		print "keyboardtyping.__exit__",exc_type,exc_val,exc_tb
	def giveshot(self): return keybtext(self)
class keybtext(shot):
	def __init__(self,eye): pass
	def __enter__(self):
		self.w = raw_input("Hej, jestem jednym stanem, daj FENa:  ")
		return self
	def __exit__(self, exc_type, exc_val, exc_tb):
		print "keybtext.__exit__",exc_type,exc_val,exc_tb