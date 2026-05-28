import cv2

# ウィンドウのタイトル
window_title = "binarize"

# コールバック関数（トラックバーが変更されたときに呼ばれる関数）
def on_trackbar(val):
    if img is not None:
        # 二値化
        # 引数: 1:画像, 2:閾値,　3閾値より大きい画素にあてるあたい, 4:二値化の方法
        # 戻り値: 適用された閾値　dst:二値化した画像
        ret, dst = cv2.threshold(img, val, 255, cv2.THRESH_BINARY)
        # 画像の表示
        cv2.imshow(window_title, dst)

# ウィンドウの作成
cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
# トラックバーの作成
cv2.createTrackbar(
    "Threshold",    # トラックバーの名前
    window_title ,  # トラックバーを表示するウィンドウのタイトル
    127,            # 初期値
    255,            # 最大値(最小値は０で固定)
    on_trackbar     # コールバック関数
    )

#入力画像のパス
img = cv2.imread("practice\\removeLine\\bad_clahe.jpg")

# トラックバーの値を取得
track_value = cv2.getTrackbarPos("Threshold", window_title)
# 最初の１回目の処理を取得した値で実行
on_trackbar(track_value)

# キー入力待ち
cv2.waitKey()