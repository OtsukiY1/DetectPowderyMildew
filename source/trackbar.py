import cv2

window_title = "CLAHE Trackbar"

# 元画像（グローバルで保持）
src = cv2.imread(
    r"C:\\Users\\abeke\\DetectPowderyMildewSpore\\dataset_25-1001-v2\\train\\images\\0022.jpg"
)

# グレースケールは一度だけ作る
gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

# =====================
# トラックバー callback
# =====================
def on_trackbar(_):
    # tileGridSize（1以上）
    tile = max(cv2.getTrackbarPos("TileSize", window_title), 1)

    # clipLimit（0.1〜10.0）
    clip_raw = cv2.getTrackbarPos("ClipLimit x10", window_title)
    clip = max(clip_raw / 10.0, 0.1)

    clahe = cv2.createCLAHE(
        clipLimit=clip,
        tileGridSize=(tile, tile)
    )
    cl1 = clahe.apply(gray)

    # パラメータ表示
    disp = cv2.cvtColor(cl1, cv2.COLOR_GRAY2BGR)
    cv2.putText(
        disp,
        f"tile={tile}, clip={clip:.1f}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.imshow(window_title, disp)

cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

cv2.createTrackbar(
    "TileSize",
    window_title,
    8,      # 初期値
    32,     # 最大値（200はデカすぎ）
    on_trackbar
)

cv2.createTrackbar(
    "ClipLimit x10",
    window_title,
    20,     # 2.0
    100,    # 10.0
    on_trackbar
)

# 初期描画
on_trackbar(0)

cv2.waitKey(0)
cv2.destroyAllWindows()
