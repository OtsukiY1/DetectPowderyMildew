from ultralytics import YOLO
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Windowsでmultiprocessingを安全に使うための処理
    
    # モデル読み込み（学習用に初期化）
    model = YOLO("yolo11m.pt")  # 例　"yolo11m.pt"

    # 学習開始
    model.train(
        #ex) data=r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\data.yaml"
        data=r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\data.yaml",  #使用するデータセットを指定する
        epochs=500,
        imgsz=640,
        patience=100, #patience=100　ー＞　アーリーストッピング100
        batch=16
    )