## DetectPowderyMildew
作成日 2026/05/28
卒研が終わったあと後継者が少しいじった状態のソースコード

__pycache__　
pythonを実行すると自動生成し，コンパイルされたモジュールが格納されている．消しても大丈夫．


## 実行方法とプログラムの説明
全てのプログラムはプロジェクトファイル(DetectPowderyMildew)に移動してから行ってください。

### source_estimation/centroid.py
重心法で感染源を求める．

実行例 python3 source/source_estimation/centroid.py

※ グラフ画像を再生成し、任意のパスに保存したい場合は、以下のように --output-plot オプションを指定して実行してください。-hオプションでヘルプ表示します。
venv/bin/python source/source_estimation/centroid.py --output-plot
