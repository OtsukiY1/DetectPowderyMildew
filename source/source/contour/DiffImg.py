import cv2
import numpy as np

# ==============================
# 1. 画像の読み込み（グレースケール）
# ==============================
originalImgPath = "practice\\removeLine\\good.jpg"
maskImgPath = "practice\\removeLine\\good_sobel.png"
orig = cv2.imread(originalImgPath, cv2.IMREAD_GRAYSCALE)
fiber = cv2.imread(maskImgPath, cv2.IMREAD_GRAYSCALE)

# 安全チェック
if orig is None or fiber is None:
    raise ValueError("画像が読み込めません。パスを確認してください。")

# ==============================
# 2. 絶対差分（繊維部分の差を強調）
# ==============================
diff = cv2.absdiff(orig, fiber)

# ==============================
# 3. 閾値処理 → 繊維マスク（線のみ抽出）
# ==============================
# → 値は調整可能（20〜60あたりを推奨）
T = 30
_, fiber_mask = cv2.threshold(diff, T, 255, cv2.THRESH_BINARY)

# fiber_mask を 0/1 に正規化
fiber_mask_norm = fiber_mask / 255.0

# ==============================
# 4. 繊維の除去（マスクで消す）
# ==============================
clean = orig * (1 - fiber_mask_norm)
clean = clean.astype(np.uint8)

# ==============================
# 5. 保存
# ==============================
cv2.imwrite("practice\\removeLine\\good_diff.png", diff)
cv2.imwrite("practice\\removeLine\\good_fiber_mask.png", fiber_mask)
cv2.imwrite("practice\\removeLine\\good_clean.png", clean)

print("差分(diff.png)、マスク(fiber_mask.png)、繊維除去(clean.png) を保存しました")
