from PyQt5.QtCore import QThread, pyqtSignal

from utils.ResultItem import ResultItem

import json


class AnalyizeThread(QThread):

    send_data_signal = pyqtSignal(ResultItem)  # 定义信号，用于发送数据

    def __init__(self, file_path: str) -> None:
        super().__init__()
        self.file_path = file_path

    def run(self) -> None:
        self.result = self.read_json(self.file_path) # get data from json file
        data = self.analyize(self.result)  # 调用analyize方法获取数据
        
        self.send_data_signal.emit(data)  # 发送数据信号

    def analyize(self, result: dict) -> ResultItem:
        if not result:
            return 
        try:
            item = result[0]
            type = item.get('type')
            if type == 'image':
                data = self.analyize_image(result)
            elif type == 'video':
                data = self.analyize_video(result)
            else:
                raise ValueError("不支持的文件类型")
        except Exception as e:
            print(f"分析数据出错: {e}")
            data = {}
        
        data["item_num"] = len(result)
        data = ResultItem(data)
        return data

    def analyize_image(self, result: dict) -> dict:
        return result[0]
    
    def analyize_video(self, result: list) -> dict:
        if not result:
            return ResultItem(None, {})
            
        path = result[0].get('path')
        final_result = {}
        category_groups = {}
        
        # 初始化类别分组
        for frame in result:
            for category in frame.get('result', {}).keys():
                if category not in category_groups:
                    category_groups[category] = {
                        'values': [],
                        'start_index': None,
                        'end_index': None
                    }
        
        # 遍历所有帧，记录每个类别的连续值
        for i, frame in enumerate(result):
            frame_result = frame.get('result', {})
            for category in category_groups.keys():
                if category in frame_result:
                    if category_groups[category]['start_index'] is None:
                        category_groups[category]['start_index'] = i
                    category_groups[category]['values'].append(frame_result[category])
                    category_groups[category]['end_index'] = i
                else:
                    # 类别中断，计算当前分组的平均值
                    if category_groups[category]['values']:
                        avg = sum(category_groups[category]['values']) / len(category_groups[category]['values'])
                        final_result[category] = final_result.get(category, 0) + avg
                        # 重置分组
                        category_groups[category]['values'] = []
                        category_groups[category]['start_index'] = None
                        category_groups[category]['end_index'] = None
        
        # 处理最后一组未完成的类别
        for category in category_groups:
            if category_groups[category]['values']:
                avg = sum(category_groups[category]['values']) / len(category_groups[category]['values'])
                final_result[category] = final_result.get(category, 0) + avg
        return {
            "path": path,
            "result": final_result
        }



    def read_json(self, file_path: str) -> list|dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(f"读取JSON文件出错: {e}")
            return {}