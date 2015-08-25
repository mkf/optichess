class UseCV2imshow(OptProcessing):
    def __init__(self,winname): 
        self.winname=winname
        import cv2
        from numpy import array as ar
    def __enter__(self): cv2.namedWindow(self.winname)
    def dajnparray(self,a): cv2.imshow(self.winname,a)
    def dajPILImage(self,b): self.dajnparray(ar(b))
    def __exit__(self,j,k,l): pass
