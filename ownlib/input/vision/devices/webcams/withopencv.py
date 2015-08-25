class WithOpenCV(Webcam):
    class CameraProb(WebcamProb):
        def __init__(self,num): self.num=int(num)
    class CameraNotOpened(CameraProb):
        def __str__(self): return "Camera %s not opened" % str(self.num)
    class CameraReadError(CameraProb):
        def __str__(self): return "Camera %s read error" % str(self.num)
    def __init__(self,camnum,rawoptlist):
        import cv2
        from PIL import Image
        self.camnum = camnum
        Webcam.__init__(self,rawoptlist)
    def __enter__(self):
        self.cap = cv2.VideoCapture(self.camnum)
        return self
    def gogonparray(self):
        if not self.cap.isopened(): raise CameraNotOpened(self.camnum)
        ret,frame=self.cap.read()
        if not ret: raise CameraReadError(self.camnum)
        return frame
    def getnparray(self):
        frame = self.gogonparray()
        self.rawoptprocnparray(frame)
        return frame
    def getPILImage(self):
        img = Image.fromarray(self.gogonparray())
        self.rawoptprocPILImage(img)
        return img
    def __exit__(self,j,k,l): pass
