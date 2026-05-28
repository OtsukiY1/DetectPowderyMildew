""""エッジ抽出する"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os

# 画像パス
img_path = "practice\\removeLine\\good.jpg"

# 保存先フォルダ
save_dir = "practice\\removeLine"
os.makedirs(save_dir, exist_ok=True)

# 画像の読み込み（グレースケール）
image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

# ノイズ除去（メディアンフィルタ）
image_blur = cv2.medianBlur(image, 5)

# Sobel フィルタ
sobel_x = cv2.Sobel(image_blur, cv2.CV_32F, 1, 0, ksize=3)
sobel_y = cv2.Sobel(image_blur, cv2.CV_32F, 0, 1, ksize=3)

# 勾配の絶対値
sobel_x_abs = cv2.convertScaleAbs(sobel_x)
sobel_y_abs = cv2.convertScaleAbs(sobel_y)

# 合成
sobel_combined = cv2.addWeighted(sobel_x_abs, 0.5, sobel_y_abs, 0.5, 0)

# --- 画像保存 ---
base = os.path.splitext(os.path.basename(img_path))[0]
#cv2.imwrite(f"{save_dir}/{base}_sobel_x.png", sobel_x_abs)
#cv2.imwrite(f"{save_dir}/{base}_sobel_y.png", sobel_y_abs)
cv2.imwrite(f"{save_dir}/{base}_sobel_combined.png", sobel_combined)

print("保存完了しました！")

# --- 可視化 ---
plt.rcParams["figure.figsize"] = [12,7.5]
plt.figure("cv2.Sobel Viewer")

plt.subplot(221)
plt.imshow(image, cmap='gray')
plt.title('Original')
plt.axis("off")

plt.subplot(222)
plt.imshow(sobel_x_abs, cmap='gray')
plt.title('Sobel X')
plt.axis("off")

plt.subplot(223)
plt.imshow(sobel_y_abs, cmap='gray')
plt.title('Sobel Y')
plt.axis("off")

plt.subplot(224)
plt.imshow(sobel_combined, cmap='gray')
plt.title('Sobel Combined')
plt.axis("off")

plt.show()