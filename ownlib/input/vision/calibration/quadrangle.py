from ..calibration import Calibration
from __future__ import division
class Quadrangle(Calibration):
    """
    Quadrangle(whiteleft,whiteright,blackleft,blackright,(((numx,numy),{whiteleft: wl,whiteright: wr,blackleft: bl, blackright: br}) for num,wl,wr,bl,br in capped/reserve)
    """
    def __init__(self,whiteleft,whiteright,blackleft,blackright,cappedfromwhite,cappedfromblack,whitereserve,blackreserve):
        self.xminymin=whiteleft;self.xmaxymin=whiteright;self.xminymax=blackright;self.xmaxymax=blackleft
        capresgen = lambda thatthing: ((i[0],{
            'xminymin':i[1]['whiteleft' if 'whiteleft' in i[1] else 'xminymin'],
            'xmaxymin':i[1]['whiteright' if 'whiteright' in i[1] else 'xmaxymin'],
            'xminymax':i[1]['blackright' if 'blackright' in i[1] else 'xminymax'],
            'xmaxymax':i[1]['blackleft' if 'blackleft' in i[1] else 'xmaxymax'],}) for i in thatthing)
        self.capfromw=capresgen(cappedfromwhite)
        self.capfromb=capresgen(cappedfromblack)
        self.whiteres=capresgen(whitereserve)
        self.blackres=capresgen(blackreserve)
        self.gend = None
    def linters(fa,fb,sa,sb):
        x1=fa[0];y1=fa[1];x2=fb[0];y2=fb=[1];x3=sa[0];y3=sa[1];x4=sb[0];y4=sb[1]
        mian = (((x1-x2)*(y3-y4))-((y1-y2)*(x3-x4)))
        if mian==0: return None
        else:
            x = (((x1*x2)-(y1*x2))*(x3-x4)-((x1-x2)*((x3*x4)-(y3*x4))))/mian
            y = (((y1*y2)-(x1*y2))*(y3-y4)-((y1-y2)*((y3*y4)-(x3*y4))))/mian
            return (x,y)
    def dajpole(self,jakie):
        return {'xminymin':xnyn,'xmaxymin':xmyn,'xminymax':xnym,'xmaxymax':xmym}
    def dajpolarescap(self,jakie):
        for i in jakie:
            assert i[0][0]!=0 and i[0][1]!=0
            if i[0][0]==1 or i[0][1]==1:
                if i[0][0]==1 and i[0][1]==1:
                    xnyn=i[1]['xminymin'];xmyn=i[1]['xmaxymin'];xnym=i[1]['xminymax'];xmym=i[1]['xmaxymax']
                    yield (0,{'xminymin':xnyn,'xmaxymin':xmyn,'xminymax':xnym,'xmaxymax':xmym})
                else:
                    pass
                    yield (nr,{'xminymin':xnyn,'xmaxymin':xmyn,'xminymax':xnym,'xmaxymax':xmym})
            else:
                pass
                yield (nr,{'xminymin':xnyn,'xmaxymin':xmyn,'xminymax':xnym,'xmaxymax':xmym})
    def genf(self):
        if self.gend is not None: return self.gend
        else:
            self.gend = {
                    'board':{(jx,jy): self.dajpole((jx,jy)) for jx in range(8) for jy in range(8)},
                    'reserve':{
                        'white':{nr: slow for nr,slow in self.dajpolarescap(self.whiteres)}
                        'black':{nr: slow for nr,slow in self.dajpolarescap(self.blackres)}}
                    'cappedfrom':{
                        'white':{nr: slow for nr,slow in self.dajpolarescap(self.capfromw)}
                        'black':{nr: slow for nr,slow in self.dajpolarescap(self.capfromb)}}
                    }
            return self.gend
