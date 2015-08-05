# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.look.eye import eye
import numpy as np
import cv2
import sane

class cam(eye):
    def __init__(self,scnr3tupl=('Mustek', '1200 UB', 'flatbed scanner'),saveraw=None,savemod=None,showraw=True,showmod=True,scanq=0,scanres=(419,584)):
        self.scnr3tupl=scnr3tupl;self.saveraw=saveraw;self.savemod=savemod;self.savinr=saveraw is not None ;self.savinm=savemod is not None, self.scanq = scanq, self.scanres = scanres
    def __enter__(self):
        if self.savinr:
            fourcc_r = cv2.VideoWriter_fourcc(*'XVID')
            self.out_r = cv2.VideoWriter(self.saveraw,fourcc_r, 0.2, self.scanres)
        if self.savinm:
            fourcc_m = cv2.VideoWriter_fourcc(*'XVID')
            self.out_m = cv2.VideoWriter(self.savemod,fourcc_m, 0.2, self.scanres)
        self.zsejninita = sane.init()
        listaprzyp = {jest[0] for jest in sane.get_devices() if jest[1:]==self.scnr3tupl}
        if len(listaprzyp)==0: raise ScannerNotFound
        elif len(listaprzyp)==1: totenjest=listaprzyp[0]
        else:
            wybrano = False
            ktorytoje = list(totenjest)
            while not wybrano:
                try:
                    totenjest=ktorytoje[1+int(raw_input(''.join([
                        'Wybierz skaner: \n',
                        ''.join([''.join(['\t',str(nje),'. ',ktorytoje[nje],' \n']) for nje in range(len(ktorytoje))]),
                        'Podaj numer z listy: '])))]
                    wybrano = True
                except ValueError: pass
                except IndexError: pass
        self.skaner = sane.open(totenjest)
        self.skaner.mode = 'Gray'
        self.skaner.resolution = scanq
        return self
    def getim(self):
        obraz = self.skaner.scan()
        arrobraz = np.array(obraz)
        if self.savinr: self.out_r.write(arrobraz)
        if showraw: cv2.imshow('raw',arrobraz)
        return arrobraz
    def __exit__(self,err_type,err_value,err_traceback):
        self.skaner.close()

class ScannerProb(Exception): pass
class ScannerNotFound(ScannerProb): pass
