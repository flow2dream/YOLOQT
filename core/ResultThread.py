from PyQt5.QtCore import QThread, pyqtSignal


class ResultThread(QThread):
    
    _instance = None
    def __init__(self):
        super().__init__()

    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def updateFormat(self, result:dict):
        pass

    def get_result(self, result:dict):
        pass