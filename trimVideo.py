import cv2
import math
from pathlib import Path
import os
import subprocess

#mp4の動画を指定のpixel数と時間で切り抜く。フレームのグレースケール化とコントラスト強調も行う。
def trimVideo(targetFileName, destFileName, startMillis, stopMillis, x_times_faster, top, bottom, left, right):
    # 動画のFPS、フレーム数・開始終了フレーム番号取得
    videoCapture = cv2.VideoCapture(targetFileName)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)
    totalFrames = int(videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # トリミング範囲のチェック
    if left < 0 or right > width or top < 0 or bottom > height:
        print("エラー: トリミング範囲が動画の範囲外です。")
        return

    startFrameIndex = math.ceil(fps * startMillis / 1000)
    stopFrameIndex = math.ceil(fps * stopMillis / 1000)
    
    if startFrameIndex < 0: 
        startFrameIndex = 0
    if stopFrameIndex >= totalFrames:
        stopFrameIndex = totalFrames - 1

    videoCapture.set(cv2.CAP_PROP_POS_FRAMES, startFrameIndex)
    frameIndex = startFrameIndex
    
    # 開始～終了地点までフレームを分割し、トリミング
    imgArr = []
    while frameIndex <= stopFrameIndex:
        ret, img = videoCapture.read()
        if not ret:
            break
        cropped_img = img[top:bottom, left:right]  # トリミング処理

        # フレームをグレースケール化
        cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
        cropped_img = contrast(cropped_img) #コントラスト強調
        cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_GRAY2BGR) #RGBに変換

        
        
        imgArr.append(cropped_img)
        frameIndex += 1
        
    # 分割フレームをmp4動画に再構成
    output_fps = fps * x_times_faster
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = None
    tmpVideoFileName = destFileName
    for img in imgArr:
        if video is None:
            h, w, _ = img.shape
            video = cv2.VideoWriter(tmpVideoFileName, fourcc, output_fps, (w, h))
        video.write(img)
    
    video.release()
    print(f"動画を '{destFileName}' に保存しました。")

#音声のない動画に音声をつける。
#
def merge_audio(original_video, target_video, target_mp4, output_video):

    #aviをmp4に変換
    subprocess.run([
    "ffmpeg",
    "-y",
    "-i", target_video, #predict/avi
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    target_mp4 #"predict/01.mp4" 
    ])
    
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


#CLAHEを用いてコントラスト強調する。
def contrast(img):
    # create a CLAHE object (Arguments are optional).
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8,8))
    cl1 = clahe.apply(img)

    return cl1

if __name__ == "__main__":
    #03.mp４から14.mp4まで二桁ゼロ埋めのファイル名を順番に処理する
    for i in range(3,14):    

        prefix          = "\\" + f"{i:02d}" #入力する動画のファイル名
        input_folder = r"c:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\movie" #入力する動画があるフォルダ
        input_filename  = input_folder + prefix + ".mp4" #入力するのファイルのパス
        output_folder = r"c:\Users\abeke\DetectPowderyMildewSpore\test\trimVideo" #出力する動画のフォルダ
        output_filename = output_folder + prefix + ".avi" #出力する動画のパス
        target_mp4 = output_folder + prefix + ".mp4"
        output_filename2 = output_folder + prefix  + "_audio.mp4"
        


        print("input_filename is ", os.path.exists(input_filename))
        print(input_filename)
        print("output_filename is ", os.path.exists(output_filename))
        
        start_time      = 0    # ms
        end_time        = 300000    # ms 秒数は大きすぎても切り詰められるので問題ない
        
        x_times_speed   = 1.0

        #顕微鏡画面のフレームサイズは1440 x 900 pixel(W\H)
        top             = 0 #0
        bottom          = 901 #901 
        left            = 0 #0
        right           = 1441 #1441
        
        trimVideo(input_filename, output_filename, 
                 start_time, end_time, 
                 x_times_speed, 
                 top, bottom,left, right
        )
        
        #input_filename: 音声ありの動画
        #output_filename: 音声なしの動画
        # mp4
        #output_filename2: 音声をつけて出力される動画
        merge_audio(input_filename, output_filename, target_mp4,
                output_filename2)


