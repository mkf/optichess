# -*- coding: utf-8 -*-
__author__ = "ArchieT"
#from ..reality import Reality,RealMove,RealFigure,RealSquare,RealBoardSquare,RealResCapdSquare,
from ..reality import *
class Steampunk(Reality):
    def __init__(self,kostkaid="00:16:53:07:F8:5B",homefilerankwheels=(0,0),filerankwheels=homefilerankwheels,filewheelr=1,rankwheelr=1,filewheeleng=100,rankwheeleng=100):
        self.filewheelr=filewheelr;self.filewheeleng=filewheeleng;self.rankwheelr=rankwheelr;self.rankwheeleng=rankwheeleng
        Reality.__init__(self,kostkaid=kostkaid,homepos=homepos)
        self.filerankwheels=filerankwheels
    def jpos(self,filerankwheels):
          pass
    def goto(self,loc):
        print "goto ",loc
