# -*- coding: utf-8 -*-
__author__ = 'ArchieT'
from ownlib.look.eye import eye
import numpy as np
import cv2

class cam(eye):
    def __init__(self,camnum,saveraw=None,savemod=None,showraw=True,showmod=True):
        self.camnum=camnum;self.saveraw=saveraw;self.savemod=savemod;self.savinr=saveraw is not None ;self.savinm=savemod is not None
    def __enter__(self):
        self.cap = cv2.VideoCapture(camnum)
        if self.savinr:
            fourcc_r = cv2.VideoWriter_fourcc(*'XVID')
            self.out_r = cv2.VideoWriter(self.saveraw,fourcc_r, 20.0, (640,480))
        if self.savinm:
            fourcc_m = cv2.VideoWriter_fourcc(*'XVID')
            self.out_m = cv2.VideoWriter(self.savemod,fourcc_m, 20.0, (640,480))
        return self
    def getim(self):
        if not self.cap.isOpened(): raise CameraNotOpened(self.camnum)
        ret,frame=self.cap.read()
        if not ret: raise CameraReadError(self.camnum)
        if self.savinr: self.out_r.write(frame)
        if showraw: cv2.imshow('raw',frame)
        return frame
    def __exit__(self,err_type,err_value,err_traceback):
        pass

class CameraProb(Exception):
    def __init__(self,num): self.num=int(num)
class CameraNotOpened(CameraProb):
    def __str__(self): return "Camera not opened: %s" % str(self.num)
class CameraReadError(CameraProb):
    def __str__(self): return "Camera read error: %s" % str(self.num)
