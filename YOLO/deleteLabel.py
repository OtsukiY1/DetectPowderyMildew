from pathlib import Path

def deleteLabel():
    # ベースディレクトリを指定
    base_dir = Path("dataset_25-1001_279")

    # 処理対象ディレクトリ（train/valid両方）
    target_dirs = [
        base_dir / "train" / "labels",
        base_dir / "valid" / "labels"
    ]

    # 各ディレクトリを順に処理
    for label_dir in target_dirs:
        if not label_dir.exists():
            print(f"⚠️ ディレクトリが存在しません: {label_dir}")
            continue

        # .txt ファイル一覧を取得
        label_files = list(label_dir.glob("*.txt"))
        print(f"\n📂 {label_dir} 内の {len(label_files)} 個のラベルファイルを処理中...")

        #各ディレクトリ単位
        for filepath in label_files:
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = []

            #各ファイル単位
            for line in lines:
                parts = line.split()
                if len(parts) == 0:
                    continue  # 空行スキップ
                
                ### 削除したいクラスの指定 ###
                if parts[0] != "1":  # クラスIDが「1」の行を削除
                
                    new_lines.append(line)
                else:
                    print(f"🗑️ 削除: {filepath.name} -> {line.strip()}")

            # ファイルに上書き保存
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        print(f"✅ {label_dir} の不要ラベルを削除しました。")

if __name__ == "__main__":
    deleteLabel()
