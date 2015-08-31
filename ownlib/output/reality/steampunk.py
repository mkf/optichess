# -*- coding: utf-8 -*-
__author__ = "ArchieT"
#from ..reality import Reality,RealMove,RealFigure,RealSquare,RealBoardSquare,RealResCapdSquare,
from ..reality import *
from math import sin,cos,radians,atan2
class Steampunk(Reality):
    DEFHOMEFILERANKWHEELS=(0,0)
    def __init__(
            self,
            kostkaid="00:16:53:07:F8:5B",
            homefilerankwheels=DEFHOMEFILERANKWHEELS,
            filerankwheels=DEFHOMEFILERANKWHEELS,
            filewheelr=1,rankwheelr=1,
            filewheeleng=100,rankwheeleng=100,
            filewheelh=1,rankwheelh=1,
            filewheelloc=0,rankwheelloc=0,
            filewheelarmlen=100,rankwheelarmlen=100):
        self.filewheelr=filewheelr
        self.filewheeleng=filewheeleng
        self.rankwheelr=rankwheelr
        self.rankwheeleng=rankwheeleng
        self.homefilerankwheels=homefilerankwheels
        self.filewheelh=filewheelh;self.rankwheelh=rankwheelh
        self.filewheelloc=filewheelloc;self.rankwheelloc=rankwheelloc
        self.filewheelarmlen=filewheelarmlen;self.rankwheelarmlen=rankwheelarmlen
        Reality.__init__(self,kostkaid=kostkaid,homepos=self.jpos(homefilerankwheels))
        self.filerankwheels=filerankwheels
    @staticmethod
    def dpos(armlen,whloc,whh,whr,wh):
        c = whr
        a = sin(radians(wh))*c
        b = cos(radians(wh))*c
        ph = whh+b
        ploc = whloc+a
        lc = armlen
        lb = ph
        la = (lc*lc)-(lb*lb)
        loc = la+ploc
        return loc
    def jpos(self,filerankwheels):
        pfile = Steampunk.dpos(self.filewheelarmlen,self.filewheelloc,self.filewheelh,self.filewheelr,filerankwheels[0])
        prank = Steampunk.dpos(self.rankwheelarmlen,self.rankwheelloc,self.rankwheelh,self.rankwheelr,filerankwheels[1])
        return (pfile,prank)
    @staticmethod
    def dang(loc,whloc,armlen,whh,whr):
        pass #it will return a set of possible angles
    @staticmethod
    def nrangchk(ang,setang):
        pass
    def goto(self,loc):
        print "goto ",loc
        fdat = Steampunk.dang(loc,self.filewheelloc,self.filewheelarmlen,self.filewheelh,self.filewheelr)
        rdat = Steampunk.dang(loc,self.rankwheelloc,self.rankwheelarmlen,self.rankwheelh,self.rankwheelr)
