import cv2
import csv
import os
import subprocess
import pygame

#音声を取得する。
def getAudio(video_path, prefix):
    print(video_path.replace(".mp4", "_audio.mp3"))
    subprocess.run([
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-q:a", "0",
        "-map", "a",
        prefix + ".mp3"
    ])
    return prefix + ".mp3"
    

prefix = "12" #ファイル名. ex)33.mp4 -> prefix = 33
video_path = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\preprosessesd" + f"\\{prefix}.mp4"
#作ったバウンディングボックスの情報（新しいラベル）が入るcsv
output_csv = r"C:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\ground_truth" + f"\\{prefix}.csv"


audio_path = getAudio(video_path, prefix)

cap = cv2.VideoCapture(video_path)
pygame.mixer.init()
pygame.mixer.music.load(audio_path)
pygame.mixer.music.play()

paused = False
bboxes = []
class_id = 0

#ファイル作成
with open(output_csv, "w", newline="") as f:
    writer = csv.writer(f)
    #writer.writerow(["frame", "x1", "y1", "x2", "y2", "class"])


while True:
    if not paused:
        ret, frame = cap.read()
        if not ret:
            break

    display = frame.copy()
    for (x, y, w, h) in bboxes:
        cv2.rectangle(display, (x1, y1), (x2, y2), (0,255,0), 2)

    cv2.imshow("Video Annotation", display)

    key = cv2.waitKey(30) & 0xFF
    

    if key == ord(' '):   # spaceで動画・音声一時停止/再開
        paused = not paused
        if paused:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
    
    
        

    elif key == ord('s') and paused:   # 停止中に s でROI(バウンディングボックス)選択
        roi = cv2.selectROI("Video Annotation", frame, fromCenter=False)
        x, y, w, h = roi
        
        x1, y1, x2, y2 = x, y, x+w, y+h
        bboxes.append((x1, y1, x2, y2))

        #CSV追記保存
        with open(output_csv, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([class_id ,x1, y1, x2, y2])


    elif key == ord('q'):   # qで終了
        break

cap.release()
pygame.mixer.quit()
cv2.destroyAllWindows()

print("Saved to:", output_csv)
