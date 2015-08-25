# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.moving.hand import hand,move,figure
class printing(hand):
	def __init__(self): print "Hej"
	def __enter__(self): return self
	def __exit__(self, exc_type, exc_val, exc_tb): print exc_type,exc_val,exc_tb
class printmove(move):
	PROPERMACHINE = printing
	def __init__(self,maszyna,typ,skad,dokad):
		assert isinstance(maszyna,printing),"not isinstance(maszyna,printing)"
		move.__init__(self,maszyna,typ,skad,dokad)
class textfigure(figure):
	PROPERMACHINE = printing
	def __init__(self,maszyna,figheight=1,pullheight=2):
		figure.__init__(self,maszyna,1.,2.)
		print self
class fR(textfigure): 
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fN(textfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fB(textfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fQ(textfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fK(textfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)
class fP(textfigure):
	FHE = 1; PHE = 2; def __init__(self,maszyna):textfigure.__init__(self,maszyna,self.FHE,self.PHE)