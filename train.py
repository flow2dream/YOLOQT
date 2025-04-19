import os, glob
from ultralytics import YOLO


if __name__ == '__main__':
    YAML_DIR = "yaml"
    DATA = "data/"
    # model = YOLO('weights/yolo11x.pt')  # Load model
    data_path = {}
    for item in os.listdir(YAML_DIR):
        data_path[YAML_DIR + "/" + item] = item.replace("-2024-9-17.yaml", "")\
                            .replace("SCB5-", "")
    print(data_path)
    for path, name in data_path.items():
        print("="*55+name+"="*55)
        nums = len(glob.glob(DATA + f"*{name}*/images/train/*.jpg"))
        if nums >= 2000:
            epochs = 200
        else: epochs = 150
        if glob.glob(f"runs/{name}/{name}/weights/last.pt"):
            model = YOLO(f"runs/{name}/{name}/weights/last.pt")
            resume = True
        else:
            model = YOLO('weights/yolo11x.pt')  # Load model
            resume = False
        print(f"数据量：{nums}\tepochs：{epochs}")
        try:
            results = model.train(
                data = path, 
                epochs = epochs, 
                batch = 0.80, 
                imgsz = 640,
                save = True,
                project = f'runs/{name}',
                save_dir = 'runs/train/{name}',
                name = name, 
                save_period = 5,
                device = 0,
                cos_lr = True,
                profile = True,
                lr0 = 0.01,
                lrf = 0.001,
                patience=20,
                resume = resume
                )
        except Exception as e:
            print(e)
            continue