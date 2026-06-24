# DetectPowderyMildew
作成日 2026/05/28
卒研が終わったあと後継者が少しいじった状態のソースコード

source_estimation/centroid.py 重心法で感染源を求める

実行方法
python3 source/source_estimation/centroid.py
※ グラフ画像を再生成し、任意のパスに保存したい場合は、以下のように --output-plot オプションを指定して実行してください。
venv/bin/python source/source_estimation/centroid.py --output-plot path/to/save_image.png
