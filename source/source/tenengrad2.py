import cv2
import numpy as np

def tenengrad_score(gray_block):
    gx = cv2.Sobel(gray_block, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray_block, cv2.CV_64F, 0, 1, ksize=3)
    return np.mean(gx**2 + gy**2)

def focus_mask(frame, block_size=64, threshold_ratio=0.3):
    """
    ピントが合っているブロックだけ残し、それ以外を黒で塗りつぶす。
    threshold_ratio: 最大スコアのX割未満のブロックを黒にする
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    score_map = np.zeros((h // block_size + 1, w // block_size + 1), dtype=np.float32)

    for row, y in enumerate(range(0, h, block_size)):
        for col, x in enumerate(range(0, w, block_size)):
            block = gray[y:y+block_size, x:x+block_size]
            if block.size == 0:
                continue
            score_map[row, col] = tenengrad_score(block)

    # 閾値以上のブロックを白(255)、未満を黒(0)にする
    threshold = score_map.max() * threshold_ratio
    binary_map = (score_map >= threshold).astype(np.uint8) * 255

    # フレームサイズに拡大（ブロック単位でくっきり拡大）
    mask = cv2.resize(binary_map, (w, h), interpolation=cv2.INTER_NEAREST)

    # マスクをBGR3チャンネルに変換して元フレームに掛ける
    mask_3ch = cv2.merge([mask, mask, mask])
    result = cv2.bitwise_and(frame, mask_3ch)
    return result

    # result = cv2.bitwise_and(frame, mask_3ch) の直後に追加
mask_blur = cv2.GaussianBlur(mask.astype(np.float32), (block_size+1|1, block_size+1|1), 0)
mask_blur = (mask_blur / 255.0)[..., np.newaxis]
result = (frame.astype(np.float32) * mask_blur).astype(np.uint8)


def process_video(video_path, output_path, block_size=64, threshold_ratio=0.3):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = focus_mask(frame, block_size=block_size, threshold_ratio=threshold_ratio)
        writer.write(result)
        if frame_idx % 100 == 0:
            print(f"{frame_idx}フレーム処理済み")
        frame_idx += 1

    cap.release()
    writer.release()
    print(f"保存完了: {output_path}")


if __name__ == "__main__":
    process_video(
        video_path=r"c:\Users\abeke\DetectPowderyMildewSpore\dataset_26-0209\movie\03.mp4",
        output_path=r"c:\Users\abeke\DetectPowderyMildewSpore\test\focused\03_masked.mp4",
        block_size=64,     # 小さいほど細かく検出（32が次の候補）
        threshold_ratio=0.3,  # 上げると黒い領域が増える、下げると減る
    )