import numpy as np
import cv2 as cv
from pathlib import Path

# =========================
# 画像1枚に対する処理を書く
# =========================

#CLAHE
def contrast(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # create a CLAHE object (Arguments are optional).
    clahe = cv.createCLAHE(clipLimit=3.5, tileGridSize=(8,8))
    cl1 = clahe.apply(img)

    return cl1

#ヒストグラム平坦化
def eqHist(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    assert img is not None, "file could not be read, check with os.path.exists()"
    equ = cv.equalizeHist(img)
    res = np.hstack((img,equ)) #stacking images side-by-side
    return res


# =========================
# ディレクトリ一括処理
# =========================
def process_directory(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_paths = sorted(
        list(input_dir.glob("*.jpg")) +
        list(input_dir.glob("*.png")) +
        list(input_dir.glob("*.jpeg"))
    )
    

    print(f"📂 {len(image_paths)} 枚の画像を処理します")

    for img_path in image_paths:
        #画像読み込み
        img = cv.imread(str(img_path))
        if img is None:
            print(f"⚠️ 読み込み失敗: {img_path.name}")
            continue
        
        #画像に行う処理
        processed = contrast(img) #CLAHE
        #processed = eqHist(img) #ヒストグラム平坦化

        out_path = output_dir / img_path.name
        cv.imwrite(str(out_path), processed)

        print(f"✔ {img_path.name}")

    print("✅ 全画像の処理が完了しました")



# =========================
# 実行
# =========================
if __name__ == "__main__":
    process_directory(
        input_dir="C:\\Users\\abeke\\DetectPowderyMildewSpore\\dataset_25-1001-v2\\valid\\images",
        output_dir="C:\\Users\\abeke\\DetectPowderyMildewSpore\\dataset_25-1001-v2\\valid\\images_processed-8-3p5"
    )
