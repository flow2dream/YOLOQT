from PyQt5.QtCore import QThread, pyqtSignal
import time
import json
import os
"""
info = {
    type: 'image' or 'video' or 'moniter',
    path: str | none
    result: {
        cls_dict: {}
    }
}
"""
TIME_FOMRAT = "%Y-%m-%d %H:%M"
BASE_DIR = "result"
class ImageResultThread(QThread):
    get_info_signal = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.get_info_signal.connect(self.get_result)
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)
    
    def run(self):
        self.updateFormat(self.result)
    
    def updateFormat(self, result:dict):
        path = result['path']
        base_name = os.path.basename(path)
        save_dir = os.path.join(BASE_DIR, result['type'])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.save_path = os.path.join(save_dir, base_name.split(".")[0]+".json")
        data = []
        # if os.path.exists(self.save_path):
        #     with open(self.save_path, 'r') as f:
        #         data = json.load(f)
        info = result['result']['cls_dict'].values()
        cls_data_cnt = {}
        for i in info:
            for j in i.split(","):
                cls_data_cnt[j] = cls_data_cnt.get(j, 0) + 1
        infos = {
            "time": time.strftime(TIME_FOMRAT, time.localtime()),
            "path": path,
            "type": result['type'],
            "result": cls_data_cnt
        }
        with open(self.save_path, "w", encoding="utf-8") as f:
            json.dump([infos], f, indent=4)
        # for item in data:
        #     if item["path"] == infos["path"]:
        #         break
        # else:
        #     data.append(infos)
        #     with open(self.save_path, 'w') as f:
        #         json.dump(data, f, indent=4)

    def get_result(self, result:dict):
        # print(result)
        self.result = result
        # self.updateFormat(result)

class VideoResultThread(QThread):
    get_info_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.get_info_signal.connect(self.get_result)
        self.infos = []
        self.mode = "PREDICT"
        self.index = 0
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)
        self.data = []
        self.result = None
        self.save_path = ""

    def run(self):
        if self.mode == "SAVE":
            with open(self.save_path, 'w') as f:
                json.dump(self.data, f, indent=4)
            self.mode = "PREDICT"
        elif self.mode == "PREDICT":
            if self.result:
                self.updateFormat(self.result)

    def updateFormat(self, result: dict):
        self.mode = result['mode']
        if self.mode == "SAVE": return
        path = result['path']
        base_name = os.path.basename(path)
        save_dir = os.path.join(BASE_DIR, result['type'])
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.save_path = os.path.join(save_dir, base_name.split(".")[0]+".json")
        if self.data == []:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    self.data = json.load(f)
        else:
            print(self.save_path)
            if self.data[-1]["path"] != path:
                self.data = []
                self.index = 0
        info = result['result']['cls_dict'].values()
        cls_data_cnt = {}
        for i in info:
            for j in i.split(","):
                cls_data_cnt[j] = cls_data_cnt.get(j, 0) + 1
        infos = {
            "time": time.strftime(TIME_FOMRAT, time.localtime()),
            "path": path,
            "type": result['type'],
            "frame_index": self.index,
            "result": cls_data_cnt
        }
        self.data.append(infos)
        self.index += 1


    def get_result(self, result: dict):
        self.result = result

    def setMode(self, mode:str):
        """
        mode: PREDICT | SAVE
        """
        self.mode = mode