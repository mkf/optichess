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
            filewheelob=1,rankwheelob=1,
            filewheeleng=100,rankwheeleng=100,
        self.rankwheelob=rankwheelob
        self.filewheelob=filewheelob
        self.filewheeleng=filewheeleng
        self.rankwheeleng=rankwheeleng
        Reality.__init__(self,kostkaid=kostkaid,homepos=homepos,pos=pos)
   def goto(self,loc):
        print "goto ",loc
