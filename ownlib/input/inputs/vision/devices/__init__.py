class Device:
    class DeviceProb(Exception): pass
    def __init__(self,rawoptlist): self.rawoptlist=rawoptlist
    def rawoptprocnparray(self,f):
        for savin in self.rawoptlist: savin.dajnparray(f)
    def rawoptprocPILImage(self,f):
        for savin in self.rawoptlist: savin.dajPILImage(f)
