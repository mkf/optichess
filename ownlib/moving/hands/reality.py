# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.moving.hand import hand,move,figure
import nxt.locator
from nxt.motor import Motor,PORT_A,PORT_B,PORT_C
class reality(hand):
	def __init__(self,kostkaid="00:16:53:07:F8:5B"):
		self.kostkaid = kostkaid
	def __enter__(self):
		self.brick = nxt.locator.find_one_brick(self.kostkaid)
		self.motx = Motor(self.brick,PORT_A)
		self.moty = Motor(self.brick,PORT_B)
		self.motz = Motor(self.brick,PORT_C)
		return self
	def __exit__(self, exc_type, exc_val, exc_tb): print exc_type,exc_val,exc_tb
class realmove(move):
	PROPERMACHINE = reality
	def __init__(self,maszyna,typ,skad,dokad):
		assert isinstance(maszyna,reality),"not isinstance(maszyna,reality)"
		move.__init__(self,maszyna,typ,skad,dokad)
class realfigure(figure):
	PROPERMACHINE = reality
	def __init__(self,maszyna,figheight,pullheight):
		assert isinstance(maszyna,reality),"not isinstance(maszyna,reality)"
		figure.__init__(self,maszyna,figheight,pullheight)
class fR(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fN(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fB(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fQ(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fK(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fP(realfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):realfigure.__init__(self,maszyna,self.FHE,self.PHE)