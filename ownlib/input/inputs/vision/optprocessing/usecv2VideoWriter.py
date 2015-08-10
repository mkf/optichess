class UseCV2VideoWriter(OptProcessing):
    def __init__(self,plik,fps,res):
        self.plik=plik,self.fps=fps,self.res=res
        import cv2
        from numpy import array as ar
    def __enter__(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(self.plik,fourcc,self.fps,self.res)
        return self
    def dajnparray(self,a): self.out.write(a)
    def dajPILImage(self,a): self.dajnparray(ar(a))
    def __exit__(self,j,k,l): pass
