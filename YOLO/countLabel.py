from pathlib import Path

def countLabel():
    # ベースディレクトリを指定
    #base_dir = Path("dataset_25-0903_845picture")
    base_dir = Path(r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_25-1001-v2\original-dataset")

    # 処理対象ディレクトリ（train/valid両方）
    target_dirs = [
        base_dir / "test" / "labels",
        base_dir / "train" / "labels",
        base_dir / "valid" / "labels"   
    ]

    for label_dir in target_dirs:
        if not label_dir.exists():
            print(f"⚠️ ディレクトリが存在しません: {label_dir}")
            continue

        # .txt ファイル一覧を取得
        label_files = list(label_dir.glob("*.txt"))
        print(f"\n📂 {label_dir} 内の {len(label_files)} 個のラベルファイルを処理中...")

        i = 0

        #txtファイル一つの処理
        for filepath in label_files:
            fileData = open(filepath,'r',encoding="utf-8")

            lines = fileData.readlines() #リストlinesに一行ずつ入る
            #print("このファイルのラベル数",len(lines)) #数を数える
            i += len(lines)#数を追加する

            fileData.close()
       
        print("フォルダ内のラベル数:",i)

    
if __name__ == "__main__":
    countLabel()
