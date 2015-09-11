# -*- coding: utf-8 -*-
__author__ = "ArchieT"
#from ..reality import Reality,RealMove,RealFigure,RealSquare,RealBoardSquare,RealResCapdSquare,
from ..reality import *
from math import sin,cos,radians,atan2
class Linear(Reality):
    DEFHOMEPOS = (0,0)
    def __init__(
            self,
            kostkaid="00:16:53:07:F8:5B",
            homepos=DEFHOMEPOS,
            pos=DEFHOMEPOS,
            filedegperone=100,
            rankdegperone=100):
        self.filedegperone=filedegperone
        self.rankdegperone=rankdegperone
        Reality.__init__(self,kostkaid=kostkaid,homepos=homepos,pos=pos)
   def goto(self,loc):
        print "goto ",loc
        movin=(loc[0]-self.pos[0],loc[1]-self.pos[1])
        self.motfile.turn(self.filedegperone*movin[0])
        self.motrank.turn(self.rankdegperone*movin[1])
        self.pos=loc
