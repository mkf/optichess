# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
class hand:
	pass
class move:
	def __init__(self,maszyna,typ,skad,dokad):
		assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
		self.maszyna = maszyna
		self.typ = typ
		self.skad = skad
		self.dokad = dokad
class figure:
	def __init__(self,maszyna,figheight,pullheight):
		assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
		self.figheight = figheight
		self.pullheight = pullheight