"""テストデータ（動画）において胞子を検出し、数をカウントし、結果の動画を出力する。

anotate.pyでテストデータの正解の胞子にアノテーションしてからcountSpore.pyを使う。
正しく検出した胞子の数（TP）を出力するが、精度が悪いため信じないこと。

    *compute_iou iouを計算する関数
    *merge_audio 出力する動画に音声をつける関数
"""

import cv2
import math
from ultralytics import YOLO
import csv
import os
import subprocess


def compute_iou(x1, y1, x2, y2, tx1, ty1, tx2, ty2):
    # 交差領域の左上と右下
    ix1 = max(x1, tx1)
    iy1 = max(y1, ty1)
    ix2 = min(x2, tx2)
    iy2 = min(y2, ty2)

    # 交差領域の幅と高さ
    inter_w = max(0, ix2 - ix1)
    inter_h = max(0, iy2 - iy1)

    # 交差面積
    inter_area = inter_w * inter_h

    # 各ボックスの面積
    box_area = (x2 - x1) * (y2 - y1)
    true_area = (tx2 - tx1) * (ty2 - ty1)

    # 和集合
    union_area = box_area + true_area - inter_area

    # IoU
    iou = inter_area / (union_area + 1e-6)

    return iou

def merge_audio(original_video, target_mp4, output_video):

    
    #音声を抽出
    subprocess.run([
        "ffmpeg",
        "-y", #確認なしで実行
        "-i", original_video, #input　#movie/mp4
        "-vn", #映像を無視
        "-acodec", "copy", #音声を再エンコードせずコピー
        "temp_audio.aac" #出力ファイル（音声のみ）
    ])

    #動画と音声を結合
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", target_mp4, #predict\mp4
        "-i", "temp_audio.aac", #入力音声
        "-c:v", "copy", #映像を再エンコードしない
        "-c:a", "copy", #音声も再エンコードしない
        "-shortest", #短いほうに合わせて切る
        output_video
    ])

    os.remove("temp_audio.aac") #一時的な音声ファイルの削除

# -----------------------------
# 設定
# -----------------------------
#ex) model = YOLO(r"C:\Users\abeke\DetectPowderyMildewSpore\runs\detect\train26-0220\weights\best.pt")
model = YOLO(r"C:\Users\abeke\DetectPowderyMildewSpore\runs\detect\train26-0220\weights\best.pt")   # あなたの学習済みモデル

#ex) prefix = "33" #ファイル名
prefix = "YOLO" #ファイル名

#ex) video_path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\preprosessesd" + f"\\{prefix}.mp4"
##video_path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\preprosessesd" + f"\\{prefix}.mp4" #入力する動画のパス
video_path = r"C:\Users\abeke\DetectPowderyMildewSpore\teat\focus\38.mp4"

#ex) input_csv = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\ground_truth" + f"\\{prefix}.csv"
##input_csv = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\ground_truth" + f"\\{prefix}.csv" #入力する動画の正解の胞子のラベル(csv)
input_csv = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\ground_truth38.csv"

###動画を保存する場所###
#ex) output_dir = r"\predict3"
output_dir = r"\predict3"

#ex) save_path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209" + output_dir +  f"\\{prefix}_result.mp4"
save_path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209" + output_dir +  f"\\{prefix}_result.mp4"
####

#新しく物体を検出したときにそのフレームを保存するディレクトリ
#ex) output_frame_dir = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209" + output_dir + f"\\{prefix}_new_object_frames"
output_frame_dir = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209" + output_dir + f"\\{prefix}_new_object_frames"
if not os.path.exists(output_frame_dir):
    os.mkdir(output_frame_dir)

threshold = 100            # 同一胞子とみなす距離（pixel）

counted_spores = []       # 既にカウントした胞子の中心座標
count = 0 #カウンタ

# -----------------------------
# 動画読み込み
# -----------------------------
cap = cv2.VideoCapture(video_path)

#正解bboxのファイルを開く
with open(input_csv) as f:
    reader = csv.reader(f)
    l = [row for row in reader] #リスト内法表記。リストlを作って開いたファイルを一行ずつlに追加する。
    #print(l[1])
for line in l:
    tclass_id, tx1, ty1, tx2, ty2 = line #正解bboxの座標
    print("line = ", line)
    
TP = 0 #True Positive 正しく検出した胞子の数
FN = 0 #False Negative 見逃した胞子の数
FP = 0 #False Positive 誤検出の数

### 動画保存用　###
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

temp_video = "temp_no_audio.mp4"
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
######

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
       break

    # -------------------------
    # YOLO推論
    # -------------------------
    results = model(frame, verbose=False)[0]
    #print("results =", results)

    detections = results.boxes  # 検出ボックス
    #print("detections = ",detections)


    # -------------------------
    # 各検出に対して処理
    # -------------------------
    for box in detections:
        #print("box =" , box)
        #検出したbboxの座標
        # bbox座標取得 (xyxy形式)
        x1, y1, x2, y2 = box.xyxy[0].tolist() #リストへ

        # 中心座標計算
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        
        new_object = True
        isSpore = True 
        conf = float(box.conf[0])
    #    print("conf = ",conf)

        # 既にカウント済みと距離比較
        for px, py in counted_spores:
            distance = math.sqrt((cx - px)**2 + (cy - py)**2)

            #print(f"NEW ({cx},{cy}) vs OLD ({px},{py}) -> dist = {distance:.2f}")
            if distance < threshold:
                new_object = False
                break

        if conf < 0.5:
            isSpore = False
            new_object = False
            
        # 新規ならカウント
        if new_object:
            count += 1
            counted_spores.append((cx, cy))

            #正解bboxの一つずつと検知したbboxのIoUを計算
            for true_bbox in l:
                tclass_id, tx1, ty1, tx2, ty2 = true_bbox
                tx1=float(tx1)
                ty1=float(ty1)
                tx2=float(tx2)
                ty2=float(ty2)

                iou = compute_iou(x1, y1, x2, y2, tx1, ty1, tx2, ty2)
                if iou >= 0.5:
                    TP += 1
                print("iou=",iou,", TP=",TP)
        

        # 可視化（緑：新規 赤：既存） #Blue, Green, Red
        color = (0, 255, 0) if new_object else (0, 0, 255)
        if not isSpore:
            color = (200, 200, 200)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.circle(frame, (cx, cy), 4, color, -1)

        label = f"{conf:.2f}"
        cv2.putText(frame, label,
                    (int(x1), int(y1)-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2)
        
        if new_object:
            cv2.imwrite(output_frame_dir + f"\\{count:03d}.png", frame)

    # -------------------------
    # カウント表示
    # -------------------------
    cv2.putText(frame, f"Count: {count}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (255, 0, 0),
                3)
    
    cv2.imshow("Spore Counter", frame)
    
    out.write(frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
merge_audio(video_path, temp_video, save_path)

print("Final Count:", count)
print(video_path, ", TP=", TP) #True Positive 正しく検出した胞子の数を返すが、精度が悪いため信じないこと。
