from pathlib import Path

#ラベルと画像の名前の対応をチェックし，それぞれのファイル数を出力する関数
#引数にデータセットのディレクトリを指定する．ex) datasets_250110_500picture
def checkImageLabelPair(base_dir):
    base_dir = Path(base_dir)

    target_dirs = [
        base_dir / "train",
        base_dir / "valid"
    ]

    for split_dir in target_dirs:
        images_dir = split_dir / "images"
        labels_dir = split_dir / "labels"

        if not images_dir.exists() or not labels_dir.exists():
            print(f"⚠️ ディレクトリが見つかりません: {split_dir}")
            continue

        # ファイル名リストを取得（拡張子を除いて比較する）
        image_names = {p.stem for p in images_dir.glob("*.jpg")}
        label_names = {p.stem for p in labels_dir.glob("*.txt")}

        # 差集合を求める
        no_label = image_names - label_names
        no_image = label_names - image_names

        print(f"\n📂 チェック対象: {split_dir}")
        print(f"画像数: {len(image_names)}　ラベル数: {len(label_names)}")

        if not no_label and not no_image:
            print("✅ すべて対応しています！")
        else:
            if no_label:
                print("⚠️ ラベルが存在しない画像:")
                for n in sorted(no_label):
                    print(f"  - {n}.jpg")
            if no_image:
                print("⚠️ 画像が存在しないラベル:")
                for n in sorted(no_image):
                    print(f"  - {n}.txt")

if __name__ == "__main__":
    checkImageLabelPair("dataset_25-1001-v2\\pre-augment")
