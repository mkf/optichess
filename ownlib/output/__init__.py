# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
class Output:
	pass
class OutputMove:
	def __init__(self,maszyna,typ,skad,dokad):
		assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
		self.maszyna = maszyna
		self.typ = typ
		self.skad = skad
		self.dokad = dokad
class OutputFigure:
	def __init__(self,maszyna,figheight,pullheight):
		assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
		self.figheight = figheight
		self.pullheight = pullheight
