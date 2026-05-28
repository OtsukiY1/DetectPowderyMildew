import cv2
import numpy as np
import os

def tenegrad_score_map(gray, block_size):
    h, w = gray.shape
    rows = h // block_size + 1
    cols = w // block_size + 1
    score_map = np.zeros((rows, cols), dtype=np.float32)
    for row, y in enumerate(range(0, h, block_size)):
        for col, x in enumerate(range(0, w, block_size)):
            block = gray[y:y+block_size, x:x+block_size]
            if block.size == 0:
                continue
            gx = cv2.Sobel(block, cv2.CV_64F, 1, 0, ksize=3)
            gy = cv2.Sobel(block, cv2.CV_64F, 0, 1, ksize=3)
            score_map[row, col] = np.mean(np.sqrt(gx**2 + gy**2))
    return score_map

def process_video(video_path, output_path, block_size=64, threshold_ratio=0.3, avg_window=10):
    avg_window
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


    print(f"[1/2] スコアマップを計算中...(全{total}フレーム)")
    all_score_maps = []
    all_frames = []
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        all_score_maps.append(tenegrad_score_map(gray, block_size))
        all_frames.append(frame)
        if idx % 100 == 0:
            print(f" {idx}/{total} フレーム処理済み")
        idx += 1
    cap.release()


    print("f[2/2] マスク適用中...(ウィンドウ={avg_window}フレーム)")
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    half = avg_window // 2

    for i, frame in enumerate(all_frames):
        start = max(0, i - half)
        end   = min(len(all_score_maps), i + half + 1)
        avg_map = np.mean(all_score_maps[start:end], axis=0)

        threshold = np.mean(avg_map) + np.std(avg_map)
        binary_map = (avg_map >= threshold).astype(np.uint8) * 255

        mask = cv2.resize(binary_map, (w, h), interpolation=cv2.INTER_NEAREST)
        mask_3ch = cv2.merge([mask, mask, mask])
        result = cv2.bitwise_and(frame, mask_3ch)
        writer.write(result)

    writer.release()
    print(f"保存完了: {output_path}")


if __name__ == "__main__":
    process_video(
       video_path=r"c:\Users\abeke\DetectPowderyMildewSpore\test\trimVideo\38.mp4",
        output_path=r"c:\Users\abeke\DetectPowderyMildewSpore\test\focused\38No2_masked.mp4",
        block_size=64,     # 小さいほど細かく検出（32が次の候補）
        threshold_ratio=0.3,  # 上げると黒い領域が増える、下げると減る
        avg_window=10,
    )