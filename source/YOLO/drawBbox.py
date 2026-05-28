import cv2
from pathlib import Path
import argparse

def visualize_yolo_bboxes(img, bboxes, color=(0, 255, 0), thickness=2):
    """YOLO形式のbboxを画像上に描画"""
    img_h, img_w = img.shape[:2]
    vis_img = img.copy()

    for cls, x, y, w, h in bboxes:
        # YOLO座標 → ピクセル座標
        x_center = x * img_w
        y_center = y * img_h
        box_w = w * img_w
        box_h = h * img_h

        x1 = int(x_center - box_w / 2)
        y1 = int(y_center - box_h / 2)
        x2 = int(x_center + box_w / 2)
        y2 = int(y_center + box_h / 2)

        # バウンディングボックスを描画
        cv2.rectangle(vis_img, (x1, y1), (x2, y2), color, thickness)

        # クラスIDを表示
        cv2.putText(vis_img, str(cls), (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    return vis_img


def draw_bboxes_from_labels(img_dir, label_dir, output_dir):
    """画像とラベルを読み込み、描画して保存する"""
    img_dir = Path(img_dir)
    label_dir = Path(label_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_path in img_dir.glob("*.jpg"):
        label_path = label_dir / f"{img_path.stem}.txt"
        if not label_path.exists():
            print(f"⚠️ ラベルが見つかりません: {label_path}")
            continue

        # 画像読み込み
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"❌ 画像が読み込めません: {img_path}")
            continue

        # ラベル読み込み
        bboxes = []
        with open(label_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    cls, x, y, w, h = parts
                    bboxes.append([cls, float(x), float(y), float(w), float(h)])

        # バウンディングボックス描画
        vis_img = visualize_yolo_bboxes(img, bboxes)

        # 保存
        out_path = output_dir / f"{img_path.stem}_vis.jpg"
        cv2.imwrite(str(out_path), vis_img)
        print(f"✅ 保存完了: {out_path}")


if __name__ == "__main__":

#    # ==== 🔧 ここを自分の環境に合わせて変更 ====
#    img_dir = input(r"入力したい画像のディレクトリを指定してください.例：C:\Users\abeke\DetectPowderyMildewSpore\datasets\train\labels"+"\n")
#    label_dir = input(r"入力したいラベルのディレクトリを指定してください.例：C:\Users\abeke\DetectPowderyMildewSpore\datasets\train\labels"+"\n")
#    output_dir = input(r"出力するディレクトリを指定してください.例：C:\Users\abeke\DetectPowderyMildewSpore\datasets\train\labels"+"\n")
#    # =============================================
#
#    draw_bboxes_from_labels(img_dir, label_dir, output_dir)

    parser = argparse.ArgumentParser(description="YOLOラベルを画像に描画して保存します。")
    parser.add_argument("--img_dir", required=True, help="画像フォルダへのパス（例: datasets/train/images）")
    parser.add_argument("--label_dir", required=True, help="ラベルフォルダへのパス（例: datasets/train/labels）")
    parser.add_argument("--output_dir", required=True, help="出力フォルダへのパス")

    args = parser.parse_args()

    draw_bboxes_from_labels(args.img_dir, args.label_dir, args.output_dir)