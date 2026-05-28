import cv2
import numpy as np
import os

cccccccccccccc



def tenengrad_score(gray_img):
    gx = cv2.Sobel(gray_img, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_img, cv2.CV_64F, 0, 1, ksize=3)
    return np.mean(gx**2 + gy**2)

def extract_focused_frames(video_path, output_dir, threshold_ratio=0.7):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    # --- 全フレームのスコアを計算 ---
    scores = []
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        scores.append(tenengrad_score(gray))
        frames.append(frame)
    cap.release()

    # --- 閾値以上のフレームだけ選ぶ ---
    scores = np.array(scores)
    threshold = scores.max() * threshold_ratio
    selected = np.where(scores >= threshold)[0]
    print(f"{len(selected)} / {len(frames)} フレームを抽出 (閾値: {threshold:.1f})")

    # --- 動画として保存 ---
    if len(selected) == 0:
        print("該当フレームなし")
        return

    h, w, _ = frames[selected[0]].shape
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    out_path = os.path.join(output_dir, "focused.mp4")
    writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    for i in selected:
        writer.write(frames[i])
    writer.release()
    print(f"保存完了: {out_path}")


if __name__ == "__main__":
    extract_focused_frames(
        video_path=r"c:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\movie\03.mp4",
        output_dir=r"c:\Users\abeke\DetectPowderyMildewSpore\test\focused",
        threshold_ratio=0.7,  # ← まずここだけ調整
    )