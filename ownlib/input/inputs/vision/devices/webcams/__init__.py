class Webcam(Device):
    class WebcamProb(DeviceProb): pass
    def __init__(self,rawoptlist): Device.__init__(self,rawoptlist)
from withopencv import WithOpenCV
