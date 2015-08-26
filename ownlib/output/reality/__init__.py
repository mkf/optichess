# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ...output import Output,OutputMove,OutputFigure,ofR,ofB,ofK,ofN,ofP,ofQ
# For now, the only real output considered will be an NXT-based machine.
import nxt.locator
from nxt.motor import Motor,PORT_A,PORT_B,PORT_C,PORT_D
class Reality(Output):
	def __init__(self,kostkaid="00:16:53:07:F8:5B"):
		self.kostkaid = kostkaid
	def __enter__(self):
		self.brick = nxt.locator.find_one_brick(self.kostkaid)
		self.motx = Motor(self.brick,PORT_A)
		self.moty = Motor(self.brick,PORT_B)
		self.motz = Motor(self.brick,PORT_C)
                self.motw = Motor(self.brick,PORT_D)
		return self
	def __exit__(self, exc_type, exc_val, exc_tb): print exc_type,exc_val,exc_tb
class RealMove(OutputMove):
	PROPERMACHINE = reality
	def __init__(self,maszyna,typ,skad,dokad):
		assert isinstance(maszyna,reality),"not isinstance(maszyna,reality)"
		move.__init__(self,maszyna,typ,skad,dokad)
class RealFigure(OutputFigure):
	PROPERMACHINE = reality
	def __init__(self,maszyna,figheight,pullheight):
		assert isinstance(maszyna,reality),"not isinstance(maszyna,reality)"
		figure.__init__(self,maszyna,figheight,pullheight)
class RealSquare(OutputSquare):
    def __init__(self,maszyna,loc):
        OutputSquare.__init__(self,maszyna)
        self.loc=loc
class RealBoardSquare(RealSquare, OutputBoardSquare):
    def __init__(self,maszyna,bsqpos,loc):
        RealSquare.__init__(self,maszyna,loc)
        OutputBoardSquare.__init__(self,maszyna,bsqpos)
class RealResCapdSquare(RealSquare, OutputResCapdSquare):
    def __init__(self,maszyna,num,loc):
        RealSquare.__init__(self,maszyna,loc)
        OutputResCapdSquare.__init__(self,maszyna,num)
class RealReserveSquare(RealResCapdSquare): pass
class RealWhiteReserveSquare(RealReserveSquare): pass
class RealBlackReserveSquare(RealReserveSquare): pass
class RealCapturedSquare(RealResCapdSquare): pass
class RealCapturedWhiteSquare(RealCapturedSquare): pass
class RealCapturedBlackSquare(RealCapturedSquare): pass
class rfR(ofR, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
class rfN(ofN, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
class rfB(ofB, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
class rfQ(ofQ, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
class rfK(ofK, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
class rfP(ofP, RealFigure):
	FHE = 1; PHE = 2
        def __init__(self,maszyna):
            RealFigure.__init__(self,maszyna,self.FHE,self.PHE)
