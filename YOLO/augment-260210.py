import albumentations as A
import cv2
from pathlib import Path
import os

# =========================
# 回転拡張
# =========================
#画像の中心を軸に回転する。
def rotate():
    
    results = []
    for angle in range(1, 360):#angle: 回転する角度。１から３５９度まで1度ずつ。

        transform = A.Compose(
            [
                A.Rotate(
                    limit=(angle, angle),
                    interpolation=cv2.INTER_LINEAR,
                    border_mode=cv2.BORDER_CONSTANT,
                    fill=0,
                    p=1.0
                )
            ],
            bbox_params=A.BboxParams(
                format="yolo",
                label_fields=["class_labels"],
                min_visibility=0.5
            )
        )

        augmented = transform(
            image=img,
            bboxes=bboxes,
            class_labels=class_labels
        )

        # bboxが消えたらスキップ
        if len(augmented["bboxes"]) == 0:
            continue

        # =========================
        # 保存
        # =========================
        stem = img_path.stem  # ファイル名の拡張子ぬいた部分。例："0002"
        suffix = f"_R_{angle:03d}" #f文字列でｇｇれ. "_R_001"みたいに3桁で0埋めする。

        # まとめて保存
        results.append({
            "augmented":augmented,
            "stem":stem,
            "suffix":suffix
        })
    
    return results

### 平行移動　###
#画像を決まったpixel数ずつずらし拡張する。
def translation():
    results = []
    
    #移動量の計算
    pA = [-1920*0.9, -1200*0.9] #最初の画像の原点
    B = [1920*0.9, 1200*0.9] #最後の画像の原点

    l = [B[0]-pA[0], B[1]-pA[1]]
    x_div = 9 #xの分割数 #10 x 10のメモリにしたいなら、マス目の数は9x9.この場合100倍に拡張できる。
    y_div = 9 #yの分割数
    x_move = l[0] / x_div #移動の間隔
    y_move = l[1] / y_div
    print("x_move=",x_move, " y_move=",y_move)

    times = 0 #処理の回数
    for i in range(y_div+1):
        y = int(pA[1] + y_move*i) #移動距離

        for j in range(x_div+1):
            x = int(pA[0] + x_move*j) #移動距離
            
            transform = A.Compose([
                A.Affine(
                    translate_px={"x":(x,x), "y":(y,y)},
                    p=1.0
                ),
                ],
                bbox_params=A.BboxParams(
                    format="yolo",
                    label_fields=["class_labels"],
                    min_visibility=0.5 #元のbboxの何%が表示されていないといけないか。この閾値を下回ると拡張後のbboxは削除される
                )
            )

            augmented = transform(
                image = img,
                bboxes = bboxes,
                class_labels = class_labels
            )

            if len(augmented["bboxes"]) == 0:
                continue

            stem = img_path.stem
            suffix = f"_T_{times:04d}"

            results.append({
                "augmented":augmented,
                "stem":stem,
                "suffix":suffix
            })
            print(f"{times}枚目を処理中...")
            times+=1

    return results

### main ###
# =========================
# 入力パス
# =========================
input_img_dir = Path(r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\preprocessed\testProglam\images")
input_label_dir = Path(r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\preprocessed\testProglam\labels")

# =========================
# 出力パス（要件どおり）
# =========================
out_img_dir = Path(
    r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\preprocessed\testProglam\output\images"
)

out_label_dir = Path(
    r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\preprocessed\testProglam\output\labels"
)

#ディレクトリ存在確認
print("out_img_dir exists?", os.path.exists(out_img_dir))
print("out_label_dir exists?", os.path.exists(out_label_dir))

images = list(input_img_dir.glob("*.jpg")) + list(input_img_dir.glob("*.png"))
print(f"{len(images)} 枚の画像を処理します")

#for文でフォルダの画像すべてに処理
for img_path in images:

    label_path = input_label_dir / f"{img_path.stem}.txt"

    if not label_path.exists():
        print(f"⚠ ラベル無し: {img_path.name}")
        continue

    # =========================
    # 画像読み込み
    # =========================
    img = cv2.imread(str(img_path))
    if img is None:
        raise RuntimeError("画像が読み込めません")

    # =========================
    # YOLOラベル読み込み
    # =========================
    bboxes = []
    class_labels = []

    with open(label_path, "r") as f:
        for line in f:
            cls, x, y, w, h = line.split()
            class_labels.append(int(cls))
            bboxes.append([float(x), float(y), float(w), float(h)])

    #各関数
    #results= rotate()
    results = translation()
    ### 保存　###
    for r in results:
        augmented = r["augmented"]
        stem = r["stem"]
        suffix = r["suffix"]

        out_img_path = out_img_dir / f"{stem}{suffix}.jpg"
        out_label_path = out_label_dir / f"{stem}{suffix}.txt"

        cv2.imwrite(str(out_img_path), augmented["image"])


        with open(out_label_path, "w") as f:
            for cls, (x, y, w, h) in zip(
                augmented["class_labels"], augmented["bboxes"]
            ):
                f.write(f"{cls} {x:.6f} {y:.6f} {w:.6f} {h:.6f}\n")

        print(f"✔ saved {out_img_path.name}")