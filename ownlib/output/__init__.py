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
	def __init__(self,maszyna):
		assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
class OutputSquare:
        def __init__(self,maszyna):
                assert 'PROPERMACHINE' in dir(self)
		assert isinstance(maszyna,self.PROPERMACHINE),"not isinstance(maszyna,%s)" % str(self.PROPERMACHINE)
class OutputBoardSquare(OutputSquare):
        def __init__(self,maszyna,bsqpos):
                OutputSquare.__init__(self,maszyna)
                self.bsqpos = bsqpos
class OutputResCapdSquare(OutputSquare):
        def __init__(self,maszyna,num):
                OutputSquare.__init__(self,maszyna)
                self.num=num
class OutputReserveSquare(OutputResCapdSquare): pass
class OutputWhiteReserveSquare(OutputReserveSquare): pass
class OutputBlackReserveSquare(OutputReserveSquare): pass
class OutputCapturedSquare(OutputResCapdSquare): pass
class OutputCapturedWhiteSquare(OutputCapturedSquare): pass
class OutputCapturedBlackSquare(OutputCapturedSquare): pass
class ofR(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
class ofN(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
class ofB(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
class ofQ(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
class ofK(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
class ofP(OutputFigure):
        def __init__(self,maszyna):OutputFigure.__init__(self,maszyna)
