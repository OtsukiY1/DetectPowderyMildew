"""ラベル付けした画像の拡張をするプログラムver.1

プログラム実行例
python source/YOLO/augmen2t.py --input dataset//preprocessed/train --output dataset/augmeted/train

"""

import albumentations as A
import cv2
from pathlib import Path
import argparse
import numpy as np

def ensure_unique_filename(path: Path):
    """同じファイル名がある場合、0からインクリメントしてユニークにする"""
    if not path.exists():
        return path
    stem, ext = path.stem, path.suffix
    n = 0
    while True:
        new_path = path.parent / f"{stem}_{n:03d}{ext}"
        if not new_path.exists():
            return new_path
        n += 1

def load_image_and_labels(img_path: Path, label_dir: Path):
    """画像とYOLOラベルを読み込む"""
    img = cv2.imread(str(img_path))
    bboxes, class_labels = [], []
    label_path = label_dir / f"{img_path.stem}.txt"
    if label_path.exists():
        with open(label_path, "r") as f:
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x, y, bw, bh = parts
                    bboxes.append([float(x), float(y), float(bw), float(bh)])
                    class_labels.append(cls)
    return img, bboxes, class_labels

def save_augmented(img, bboxes, class_labels, out_dir_img: Path, out_dir_lbl: Path, stem_suffix: str, original_stem: str):
    """画像とラベルを保存"""
    # 画像
    out_img_path = ensure_unique_filename(out_dir_img / f"{original_stem}{stem_suffix}.jpg")
    cv2.imwrite(str(out_img_path), img)
    # ラベル
    out_lbl_path = ensure_unique_filename(out_dir_lbl / f"{original_stem}{stem_suffix}.txt")
    with open(out_lbl_path, "w") as f:
        for cls, (x, y, bw, bh) in zip(class_labels, bboxes):
            f.write(f"{cls} {x:.6f} {y:.6f} {bw:.6f} {bh:.6f}\n")
    print(f"✅ 保存: {out_img_path}, {out_lbl_path}")

# ---------- データ拡張関数 ----------
def horizontal_flip(img, bboxes, class_labels):
    """
    平行移動。デフォルトではランダムに20%の平行移動。
    :param img: 入力画像
    """
   
    transform = A.Compose([A.HorizontalFlip(p=1.0)], #pは平行移動する確率, 0~1
                           bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
    aug = transform(image=img, bboxes=bboxes, class_labels=class_labels)
    return aug["image"], aug["bboxes"], aug["class_labels"]

def vertical_flip(img, bboxes, class_labels):
    """垂直反転する。"""
    transform = A.Compose([A.VerticalFlip(p=1.0)], bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
    aug = transform(image=img, bboxes=bboxes, class_labels=class_labels)
    return aug["image"], aug["bboxes"], aug["class_labels"]

def brightness_contrast(img, bboxes, class_labels, n=0):
    """明るさとコントラストを限られた範囲でランダムに変える。"""
    transform = A.Compose([A.RandomBrightnessContrast(p=1.0)], bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
    aug = transform(image=img, bboxes=bboxes, class_labels=class_labels)
    return aug["image"], aug["bboxes"], aug["class_labels"], f"_BC_{n:04d}"

#def rotate(img, bboxes, class_labels, n=0):
#    #limitで角度範囲指定（度）.デフォルト:30.ｐは処理する確率
#    transform = A.Compose([A.Rotate(limit=30, p=1.0)], bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
#    aug = transform(image=img, bboxes=bboxes, class_labels=class_labels)
#    return aug["image"], aug["bboxes"], aug["class_labels"], f"_R_{n:04d}"

#n：ファイル名の連番
def rotate(angle, img, bboxes, class_labels, n=0):
    """:param angle: 拡張する角度"""
    transform = A.Rotate(
        limit=(angle, angle),
        interpolation=cv2.INTER_LINEAR,
        border_mode=cv2.BORDER_REFLECT,
        p=1.0
    )
    aug = transform(image = img, bboxes=bboxes, class_labels=class_labels)
    return aug["image"], aug["bboxes"], aug["class_labels"], f"_R_{n:04d}"


def translate(img, bboxes, class_labels, n=0, shift_limit=0.2):
    """画像を平行移動 (shift_limit=移動割合, 例: 0.2なら±20%の範囲で移動)"""
    transform = A.Compose([
        A.ShiftScaleRotate(shift_limit=shift_limit, scale_limit=0, rotate_limit=0, p=1.0)
    ], bbox_params=A.BboxParams(format="yolo", label_fields=["class_labels"]))
    
    aug = transform(image=img, bboxes=bboxes, class_labels=class_labels)
    return aug["image"], aug["bboxes"], aug["class_labels"], f"_T_{n:04d}"

#切り抜きと拡大。
def crop_and_zoom(img, bboxes, class_labels, n=0, crop_w=960, crop_h=600, scale=2.0):
    """
    アノテーションを含む範囲を切り出し、2倍に拡大して保存用データを返す
    """
    h, w = img.shape[:2]
    bboxes_abs = []

    # YOLO座標 -> ピクセル座標変換
    for (x, y, bw, bh) in bboxes:
        cx, cy = x * w, y * h
        bw, bh = bw * w, bh * h
        x1, y1 = int(cx - bw / 2), int(cy - bh / 2)
        x2, y2 = int(cx + bw / 2), int(cy + bh / 2)
        bboxes_abs.append([x1, y1, x2, y2])

    # 1つ目の物体を中心にクロップ領域を決定（全BBoxでも拡張可）
    if len(bboxes_abs) == 0:
        return img, bboxes, class_labels, f"_ZOOM_{n:04d}"  # 何もなければスキップ

    x_min = min(b[0] for b in bboxes_abs)
    y_min = min(b[1] for b in bboxes_abs)
    x_max = max(b[2] for b in bboxes_abs)
    y_max = max(b[3] for b in bboxes_abs)

    # 物体を中央に配置したクロップ範囲を決定
    cx, cy = (x_min + x_max) // 2, (y_min + y_max) // 2
    crop_x1 = max(0, cx - crop_w // 2)
    crop_y1 = max(0, cy - crop_h // 2)
    crop_x2 = min(w, crop_x1 + crop_w)
    crop_y2 = min(h, crop_y1 + crop_h)

    # 範囲を再調整（右下は固定、左上が画像外なら戻す）
    if crop_x2 - crop_x1 < crop_w:
        crop_x1 = max(0, crop_x2 - crop_w)
    if crop_y2 - crop_y1 < crop_h:
        crop_y1 = max(0, crop_y2 - crop_h)

    # クロップ
    cropped = img[crop_y1:crop_y2, crop_x1:crop_x2]

    # 2倍に拡大
    zoomed = cv2.resize(cropped, (int(crop_w * scale), int(crop_h * scale)))

    # BBox座標をクロップ後に再計算
    new_bboxes = []
    for (x1, y1, x2, y2) in bboxes_abs:
        # クロップ内での相対位置
        nx1 = (x1 - crop_x1) * scale
        ny1 = (y1 - crop_y1) * scale
        nx2 = (x2 - crop_x1) * scale
        ny2 = (y2 - crop_y1) * scale

        # 切り出し範囲外ならスキップ
        if nx2 < 0 or ny2 < 0 or nx1 > crop_w * scale or ny1 > crop_h * scale:
            continue

        # YOLO座標に戻す
        new_cx = ((nx1 + nx2) / 2) / (crop_w * scale)
        new_cy = ((ny1 + ny2) / 2) / (crop_h * scale)
        new_bw = (nx2 - nx1) / (crop_w * scale)
        new_bh = (ny2 - ny1) / (crop_h * scale)
        new_bboxes.append([new_cx, new_cy, new_bw, new_bh])

    return zoomed, new_bboxes, class_labels, f"_ZOOM_{n:04d}"



# ---------- メイン関数 ----------
def main(Input_dir, output_dir):
    Input_dir = Path(Input_dir)
    output_dir = Path(output_dir)

    input_img_dir = Input_dir / "images_processed-8-3p5"
    input_lbl_dir = Input_dir / "labels"
    output_img_dir = output_dir / "images"
    output_lbl_dir = output_dir / "labels"
    output_img_dir.mkdir(parents=True, exist_ok=True)
    output_lbl_dir.mkdir(parents=True, exist_ok=True)

    for img_path in input_img_dir.glob("*.jpg"):
        img, bboxes, class_labels = load_image_and_labels(img_path, input_lbl_dir)
        stem = img_path.stem

        #1. 水平反転
        #hf_img, hf_bboxes, hf_labels = horizontal_flip(img, bboxes, class_labels)
        #save_augmented(hf_img, hf_bboxes, hf_labels, output_img_dir, output_lbl_dir, "_HF", stem)

        #2. 垂直反転
        #vf_img, vf_bboxes, vf_labels = vertical_flip(img, bboxes, class_labels)
        #save_augmented(vf_img, vf_bboxes, vf_labels, output_img_dir, output_lbl_dir, "_VF", stem)

        # 3. 明るさ・コントラスト変更
        #for i in range(2):  # 例: 3パターン
        #   bc_img, bc_bboxes, bc_labels, suffix = brightness_contrast(img, bboxes, class_labels, n=i)
        #   save_augmented(bc_img, bc_bboxes, bc_labels, output_img_dir, output_lbl_dir, suffix, stem)

        #4. 回転
        #for i in range(1):  # 例: 3パターン
        #    r_img, r_bboxes, r_labels, suffix = rotate(img, bboxes, class_labels, n=i)
        #    save_augmented(r_img, r_bboxes, r_labels, output_img_dir, output_lbl_dir, suffix, stem)

        # 1~359度の範囲で一度ずつ回転
        for angle in range(1, 359):

            r_img, r_bboxes, r_labels, suffix = rotate(angle, img, bboxes, class_labels, n=i)
            save_augmented(r_img, r_bboxes, r_labels, output_img_dir, output_lbl_dir, suffix, stem)

        # 5. 平行移動
        #for i in range(2):  # 例: 3パターン生成
        #    t_img, t_bboxes, t_labels, suffix = translate(img, bboxes, class_labels, n=i, shift_limit=0.2)
        #    save_augmented(t_img, t_bboxes, t_labels, output_img_dir, output_lbl_dir, suffix, stem)

        # 6. アノテーション領域を含むズーム拡大
        #for i in range(1):  # 例: 2パターン生成
        #    zoom_img, zoom_bboxes, zoom_labels, suffix = crop_and_zoom(img, bboxes, class_labels, n=i)
        #    save_augmented(zoom_img, zoom_bboxes, zoom_labels, output_img_dir, output_lbl_dir, suffix, stem)

# ---------- コマンドライン実行 ----------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, help="Input directory containing images/ and labels/")
    parser.add_argument("--output", type=str, required=True, help="Output directory for augmented images/ and labels/")
    args = parser.parse_args()
    main(args.input, args.output)
