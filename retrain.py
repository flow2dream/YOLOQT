import os, glob
from ultralytics import YOLO


if __name__ == '__main__':
    DATA = "dataset/"
    YAML_DIR = os.path.join(DATA, "yaml")
    # model = YOLO('weights/yolo11x.pt')  # Load model
    data_path = []
    for item in os.listdir(YAML_DIR):
        data_path.append(os.path.join(YAML_DIR, item))
    for path in data_path:
        base_name:str = os.path.basename(path)
        name = base_name.replace(".yaml", "")
        print(name)
        print("="*55+name+"="*55)
        if glob.glob(f"retrain_runs/{name}/{name}/weights/last.pt"):
            model = YOLO(f"retrain_runs/{name}/{name}/weights/last.pt")
            resume = True
        else:
            model = YOLO('weights/yolo11x.pt')  # Load model
            resume = False
        try:
            results = model.train(
                data = path, 
                epochs = 500, 
                batch = 0.80, 
                imgsz = 640,
                save = True,
                project = f'retrain_runs/{name}',
                save_dir = 'retrain_runs/train/{name}',
                name = name, 
                save_period = 5,
                device = 0,
                cos_lr = True,
                profile = True,
                lr0 = 0.01,
                lrf = 0.001,
                patience=20,
                resume = resume,
                optimizer = "SGD",
                momentum = 0.9,
                )
        except Exception as e:
            print(e)
            continue