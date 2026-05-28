"""
楕円フィッティングにより胞子を検出する。ゼミ１０回目で使ったもの。
"""

from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng

prefix = "sporeTest"
version = "_0"
input_folder = "practice\\removeLine\\"
output_folder = "practice\\removeLine\\handout\\"
output_filename = output_folder + prefix + version

rng.seed(12345)

def calcCircularity(contour):
    '''
    円形度を求める

    Parameters
    ----------
    contour : ndarray
        輪郭の(x,y)座標の配列

    Returns
    -------
        円形度

    '''
    # 面積
    area = cv.contourArea(contour)
    # 周囲長
    length = cv.arcLength(contour, True)

    # 円形度を返す
    return 4*np.pi*area/length/length

def thresh_callback(val):
    global output_filename
    threshold = val
    
    #ret: 輪郭画像
    # 1: 2:minVal 3:maxVal
    canny_output = cv.Canny(src_gray, threshold, threshold * 2)

    output_filename += "_canny"
    cv.imwrite(output_filename + ".jpg", canny_output)

    #ret:　contours: 輪郭.List[numpy.ndarray]
    #1:2値画像　2:輪郭構造の取得方法。輪郭の階層情報をツリー形式で取得します　3:輪郭座標の取得方法。縦、横、斜め45°方向に完全に直線の部分の輪郭の点を省略。
    contours, _ = cv.findContours(canny_output, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    #カラー画像に変換
    dbg = cv.cvtColor(canny_output, cv.COLOR_GRAY2BGR)
    #輪郭描画 ret: 画像(numpy.ndarray)
    #3:負の値ですべての輪郭描写　4:線の色 5:線の太さ。ー１で塗りつぶし
    cv.drawContours(dbg, contours, -1, (0,255,0), 2)
    cv.imshow("contours", dbg) #出力
    output_filename += "_contours"
    cv.imwrite(output_filename + ".jpg", dbg)
    
    cv.waitKey(0) #キーボードが押されるまで処理を待つ

    print("size of contours is", len(contours)) 
    # Find the rotated rectangles and ellipses for each contour
    minRect = [None]*len(contours) #最小外接矩形の入れ物
    minEllipse = [None]*len(contours) #楕円の入れ物。 []*n ｰ>n個の要素のリストを作る
    #print("minRect is ", minRect, "minEllipse is ", minEllipse)
    for i, c in enumerate(contours): #iはインデックス, cはcontour
        minRect[i] = cv.minAreaRect(c)
        area = cv.contourArea(c)
        
        #print("minRect is ", minRect, "\nminEllipse is ", minEllipse,  "\ni is ", i, "\nc is ",c)
        if c.shape[0] > 5: # and 1000 < area < 2000:
            minEllipse[i] = cv.fitEllipse(c) #楕円の最小外接矩形を返す

    # Draw contours + rotated rects + ellipses

    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    for i, c in enumerate(contours):
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        # contour
        cv.drawContours(drawing, contours, i, color)
        # ellipse
        if c.shape[0] > 5:
            cv.ellipse(drawing, minEllipse[i], color, 2)
        # rotated rectangle
        box = cv.boxPoints(minRect[i])
        box = np.intp(box) #np.intp: Integer used for indexing (same as C ssize_t; normally either int32 or int64)
        #cv.drawContours(drawing, [box], 0, color)
    cv.imwrite(output_filename + "_rects.jpg", drawing)
    #cv.imshow('Contours2', drawing)


        
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)

    # 楕円描画
    #print("Ellipses is ", minEllipse)
    i = 0 #フィルタ後の楕円数カウンタ
    for idx, ellipse in enumerate(minEllipse):

        # 楕円が None の場合スキップ
        if ellipse is None:
            continue

        # 対応する contour
        c = contours[idx]

        (cx, cy), (minor, major), angle = ellipse
        mi_ma_flag = False
        cir_flag = False
        area_flag = False

        # ---- 長短比フィルタ例 ----
        if 0.2 <= (minor/major) <= 0.8:
            mi_ma_flag = True

        # ---- 円形度フィルタ ----
        # 円形度計算
        circularity = calcCircularity(c) #contour(元の輪郭)の円形度
        if circularity < 0.7:
            cir_flag = True

        # ---- 面積フィルタ ----
        area = cv.contourArea(c)
        if  500 < area:
            area_flag = True

        #print("mi_ma is " , minor/major, "cir is ", circularity, "area is ",area) #"mi_ma_flag is ", mi_ma_flag, "cir_flag is ", cir_flag, 
        
        
        # 楕円を描画
        if mi_ma_flag and cir_flag and area_flag:
            # cv2.ellipse(img, box, color, thickness=1, lineType=cv2.LINE_8) 
            # 引数boxは(center, axes, angle)で表し、centerは(x, y)、axesは(横方向直径, 縦方向直径)、回転角度angleはx軸方向を0度として時計回りに度で指定する。
            cv.ellipse(drawing, ellipse, color, 2)
            # 輪郭の矩形領域
            x, y, w, h = cv.boundingRect(c)
            # 円形度描画
            cv.putText(drawing, f"{circularity:.3f}", (x, y+30),
                    cv.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 1, cv.LINE_AA)
            i += 1
        
    print("フィルタ後の楕円数：", i)
    cv.imshow('ellipse', drawing)
    cv.imwrite(output_filename + "_ellipse.jpg", drawing)

#parser = argparse.ArgumentParser(description='Code for Creating Bounding rotated boxes and ellipses for contours tutorial.')
#parser.add_argument('--input', help='Path to input image.', default='stuff.jpg')
#args = parser.parse_args()

#src = cv.imread(cv.samples.findFile(args.input))
#if src is None:
#    print('Could not open or find the image:', args.input)
#    exit(0)



src = cv.imread(input_folder + prefix + ".png")

# Convert image to gray and blur it
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)
output_filename += "_gray"
cv.imwrite(output_filename + ".jpg", src_gray)

# フィルタサイズの設定
d = 5
# 色空間におけるフィルタの標準偏差の設定
sigmaColor = 75
# 座標空間におけるフィルタの標準偏差の設定
sigmaSpace = 75
# バイラテラルフィルタの適用
blurred = cv.bilateralFilter(src_gray, d, sigmaColor, sigmaSpace)
output_filename += "_bilateral"
cv.imwrite(output_filename + ".jpg", blurred)

#CLAHE
clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
cl1 = clahe.apply(blurred)
output_filename += "_clahe"
cv.imwrite(output_filename + ".jpg",cl1)

source_window = 'Source'
cv.namedWindow(source_window)
cv.imshow(source_window, src)

max_thresh = 255
thresh = 100 # initial threshold
cv.createTrackbar('Canny Thresh:', source_window, thresh, max_thresh, thresh_callback)
thresh_callback(thresh)

cv.waitKey()