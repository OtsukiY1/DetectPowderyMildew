from pathlib import Path
import cv2

def convert_to_grayscale(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    images = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
    print(f"📂 {len(images)} 枚の画像を処理します")

    for img_path in images:
        img = cv2.imread(str(img_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        save_path = output_dir / img_path.name
        cv2.imwrite(str(save_path), gray)

    print("✅ すべての画像をグレースケールに変換しました")

# 使用例
convert_to_grayscale("dataset\\img", "dataset\\grayImg")
