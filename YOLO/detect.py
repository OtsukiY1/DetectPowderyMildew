from ultralytics import YOLO
from pathlib import Path

# 1. 学習済みモデルをロード
model = YOLO(r"C:\Users\abeke\DetectPowderyMildewSpore\runs\detect\train26-0220\weights\best.pt")

# 2. 入出力ディレクトリの指定
# (研究室のPC)
input_dir = Path(r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\preprosessesd\14.mp4")
output_dir = Path(r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\predict3")


# 3. 推論の実行
results = model.predict(
    source=str(input_dir),   # 入力フォルダ全体を指定
    save=True,               # 検出結果を画像として保存
    save_txt=False,          # YOLO形式のtxtは不要ならFalse（必要ならTrue）
    project=str(output_dir.parent), # 出力の親ディレクトリ
    name=output_dir.name,    # 出力フォルダ名
    exist_ok=True            # 既存フォルダに上書きOK
)

print(f"✅ 検出結果を保存しました: {output_dir}")
