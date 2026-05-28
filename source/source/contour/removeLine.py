# 直線を検出する。ゼミで使ったもの。

import cv2
import numpy as np

prefix = "\\bad"
version = "_1"
input_folder = "practice\\removeLine"
output_folder = "practice\\removeLine\\hough"
output_filename = output_folder + prefix + version

img = cv2.imread(input_folder + prefix + ".jpg")

#gray scale
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
output_filename += "_gray"
cv2.imwrite(output_filename + ".jpg", gray)

# ノイズ除去
# フィルタサイズの設定
d = 5
# 色空間におけるフィルタの標準偏差の設定
sigmaColor = 75
# 座標空間におけるフィルタの標準偏差の設定
sigmaSpace = 75
# バイラテラルフィルタの適用
img = cv2.bilateralFilter(gray, d, sigmaColor, sigmaSpace)
output_filename += "_bilateral"
cv2.imwrite(output_filename + ".jpg", img)

#### コントラストを強くする
# create a CLAHE object (Arguments are optional).
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
cl1 = clahe.apply(img)
output_filename += "_clahe"
cv2.imwrite(output_filename + ".jpg",cl1)
img = cl1
####

# 二値化　ret：適用された閾値、th：画像
#ret, th = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
#output_filename += "_binary"
#cv2.imwrite(output_filename + ".jpg",th)

# エッジ検出　Canny検出器
edges = cv2.Canny(img,50,150,apertureSize = 3)
output_filename += "_edges"
cv2.imwrite(output_filename + ".jpg",edges)

#### sobel filter ####

#Sobelフィルタを適用
#sobel_x = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=5)               # 水平方向の勾配
#sobel_y = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=5)               # 垂直方向の勾配
# 勾配の絶対値を計算
#sobel_x = cv2.convertScaleAbs(sobel_x)
#sobel_y = cv2.convertScaleAbs(sobel_y)
# 水平方向と垂直方向の勾配を組み合わせて合成勾配を計算
#edges = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)
####

#ハフ変換の閾値
minLineLength = 100
maxLineGap = 10
lines = cv2.HoughLinesP(edges,1,np.pi/180,30,minLineLength,maxLineGap)

print(len(lines))
######

#描画
img = cv2.cvtColor(edges,cv2.COLOR_GRAY2BGR)

for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(img, (x1,y1), (x2,y2), (0,255,0), 2)
output_filename += "_hough"
cv2.imwrite(output_filename + '.jpg',img)

