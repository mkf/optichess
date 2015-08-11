class SavePNG(OptProcessing):
    def __init__(self,katalog):
        import os, os.path
        from time import time
        from PIL import Image
        self.kat = os.path.abspath(os.path.realpath(katalog))
    def __enter__(self):
        lodir = lambda: os.path.abspath(
                os.path.realpath(
                    os.path.join(
                        self.kat,
                        'savepngdir'+\
                                str(
                                    int(
                                        time()
                                        )
                                    )
                                )
                    )
                )
        self.odir = lodir()
        try: os.mkdir(self.odir)
        except OSError:
            try:
                self.odir = lodir()
                os.mkdir(self.odir)
            except OSError:
                try:
                    self.odir=lodir()
                    os.mkdir(self.odir)
                except OSError:
                    self.odir=lodir()
                    os.mkdir(self.odir)
    def dajPILImage(self,a):
        a.save(
                os.path.abspath(
                    os.path.realpath(
                        os.path.join(
                            self.odir,
                            'savepng'+\
                                    str(
                                        int(
                                            time()
                                            )
                                        )+'.png'
                                    )
                        )
                    )
                )
    def dajnparray(self,b): self.dajpilimage(Image.fromarray(b))
    def __exit__(self,j,k,l): pass
