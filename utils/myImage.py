from PyQt5.QtGui import QPixmap
class myImage:

    path = None
    image = None
    
    def __init__(self, path:str, image:QPixmap):
        self.path = path
        self.image = image
