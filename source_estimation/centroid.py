#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Infection Source Estimation using Centroid (Center of Gravity) Method.
This script calculates the estimated coordinates of the powdery mildew infection source
based on air spore count measurements at multiple sensor locations.
"""

import os
import argparse
import matplotlib.pyplot as plt
import csv
import pprint
from DataPointCombination import DataPointCombination

# Greenhouse Dimensions (default config)
GREENHOUSE_WIDTH = 6.28   # x-axis (meters)
GREENHOUSE_LENGTH = 10.01 # y-axis (meters)

# Default Sensor Layout and Spore Counts (C_i)
# Coordinates are in meters relative to the bottom-left corner of the house (0, 0)
SENSORS = [
    {"id": "A", "name": "Bottom-Left (左下)", "x": 1.45, "y": 2.52, "spore_count": 0},
    {"id": "B", "name": "Top-Left (左上)", "x":1.45 , "y": GREENHOUSE_LENGTH - 2.36, "spore_count": 0},
    {"id": "C", "name": "Bottom-Right (右下)", "x": GREENHOUSE_WIDTH - 1.76, "y": 2.52, "spore_count": 0},
    {"id": "D", "name": "Top-Right (右上)", "x": GREENHOUSE_WIDTH - 1.76, "y": GREENHOUSE_LENGTH - 2.36, "spore_count": 0},
    {"id": "E", "name": "Center (真ん中)", "x":2.97, "y":5.68, "spore_count": 0},
]

# True Infection Source (for comparison/validation)
TRUE_SOURCE = {"x": 3.23, "y": 5.50}


def estimate_source(sensors):
    """
    Calculate the estimated source coordinates (x_s, y_s) using the centroid formula:
    x_s = sum(C_i * x_i) / sum(C_i)
    y_s = sum(C_i * y_i) / sum(C_i)
    """
    total_spore_count = sum(s["spore_count"] for s in sensors)
    
    if total_spore_count == 0:
        raise ValueError("Total spore count is 0. Cannot estimate source using centroid method.")
        
    sum_cx = sum(s["spore_count"] * s["x"] for s in sensors)
    sum_cy = sum(s["spore_count"] * s["y"] for s in sensors)
    
    x_s = sum_cx / total_spore_count
    y_s = sum_cy / total_spore_count
    
    return x_s, y_s, total_spore_count


def plot_simulation(width, length, sensors, est_x, est_y, true_x, true_y, save_path=None):
    """
    Generate a 2D layout plot of the greenhouse, sensors, true source, and estimated source.
    """
    plt.figure(figsize=(6, 10))
    
    # 1. Plot greenhouse boundaries
    plt.plot([0, width, width, 0, 0], [0, 0, length, length, 0], 'k-', linewidth=2, label="Greenhouse Boundary")
    
    # 2. Plot sensors
    # Scatter plot with size proportional to spore count (add a baseline size so 0 spore count is still visible)
    sensor_x = [s["x"] for s in sensors]
    sensor_y = [s["y"] for s in sensors]
    spore_counts = [s["spore_count"] for s in sensors]
    
    # Size logic: minimum size 100, increases by 200 per spore
    #sizes = [100 + 200 * c for c in spore_counts]
    sizes = 100
    
    # Plot sensor points
    sc = plt.scatter(sensor_x, sensor_y, s=sizes, c=spore_counts, cmap='Reds', edgecolors='black', zorder=5, label="Sensors (size ~ spore count)")
    
    # Add spore count text label next to each sensor
    for s in sensors:
        plt.text(s["x"] + 0.25, s["y"], f"S{s['id']}\nC={s['spore_count']}", 
                 fontsize=10, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, boxstyle='round,pad=0.2'))
        
    # 3. Plot True infection source
    plt.scatter(true_x, true_y, color='green', marker='*', s=250, edgecolors='black', zorder=6, label=f"True Source ({true_x:.2f}, {true_y:.2f})")
    
    # 4. Plot Estimated infection source
    plt.scatter(est_x, est_y, color='blue', marker='X', s=250, edgecolors='black', zorder=6, label=f"Estimated Source ({est_x:.2f}, {est_y:.2f})")
    
    # Draw a dashed line between True Source and Estimated Source to visualize error
    plt.plot([true_x, est_x], [true_y, est_y], 'b--', linewidth=1.5, label=f"Error Distance: {((true_x - est_x)**2 + (true_y - est_y)**2)**0.5:.2f}m")
    
    # Formatting
    plt.title("Powdery Mildew Source Estimation (Centroid Method)", fontsize=12, pad=15)
    plt.xlabel("Width (m)", fontsize=10)
    plt.ylabel("Length (m)", fontsize=10)
    plt.xlim(-1, width + 1)
    plt.ylim(-1, length + 1)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.colorbar(sc, label="Spore Count (C_i)", orientation='horizontal', pad=0.25, shrink=0.5, aspect=40)
    plt.legend(loc='upper right', bbox_to_anchor=(1.0, -0.1))
    plt.tight_layout()
    
    if save_path:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved successfully to: {save_path}")
        
    plt.close()

#そのうち発生源を予測するクラスとしてmain関数を別に実装するといい？？
def print_error_table(days, combinations, error_list):
    """
    誤差の結果を組み合わせ別に表形式で出力する。
    また、各組み合わせの平均誤差も計算して表示する。
    """
    print("\n=== Error Table (Row: Day, Column: Combination) ===")
    comb_names = ["-".join(comb) for comb in combinations]
    
    # ヘッダー（組み合わせ名）を出力
    header = f"{'Date':<12} | " + " | ".join([f"{name:^8}" for name in comb_names])
    print(header)
    print("-" * len(header))
    
    # 各日付の誤差データを整形して出力
    for i, day in enumerate(days):
        row_errors = error_list[i]
        formatted_row = []
        for err in row_errors:
            if err is None:
                formatted_row.append(f"{'N/A':^8}")
            else:
                formatted_row.append(f"{err:^8.3f}")
        print(f"{day:<12} | " + " | ".join(formatted_row))
        
    print("-" * len(header))
    
    # 組み合わせごとに平均（Average）を計算する
    average_errors = []
    num_combinations = len(combinations)
    
    for col_idx in range(num_combinations):
        valid_errors = [
            error_list[row_idx][col_idx] 
            for row_idx in range(len(days)) 
            if error_list[row_idx][col_idx] is not None
        ]
        
        if valid_errors:
            avg = sum(valid_errors) / len(valid_errors)
        else:
            avg = None
        average_errors.append(avg)
        
    # 平均値を出力
    formatted_avg = []
    for avg in average_errors:
        if avg is None:
            formatted_avg.append(f"{'N/A':^8}")
        else:
            formatted_avg.append(f"{avg:^8.3f}")
    print(f"{'Average':<12} | " + " | ".join(formatted_avg))


def main():
    parser = argparse.ArgumentParser(description="Infection Source Estimation") #コマンドライン引数argsのパーサをつくる
    parser.add_argument("--output-plot", type=str, default=None, help="Path to save the generated visualization plot")# オプション引数を追加
    args = parser.parse_args() #引数を解析
    
    print("=== Powdery Mildew Infection Source Estimation (Centroid Method) ===")
    print(f"Greenhouse Dimensions: {GREENHOUSE_WIDTH}m (Width) x {GREENHOUSE_LENGTH}m (Length)")
    print(f"True Infection Source Coordinate: ({TRUE_SOURCE['x']}, {TRUE_SOURCE['y']})")
   
    # 胞子数をcsvから読み込む
    csv_path = "spore_num/num_of_spore.csv"
    with open(csv_path) as f:
        reader = csv.reader(f)
        
        # ヘッダー行を読み飛ばす
        next(reader)
        
        dp_comb = DataPointCombination()
        combinations = dp_comb.get_combinations()
        
        # 推定と正解の誤差の二次元リスト（行＝日、列＝組み合わせ）
        error_list = []
        days = []

        # 全ての日を処理する繰り返し
        for row in reader:
            if not row:
                continue
            
            day = row[0]
            days.append(day)
            print(f"\n=== Day: {day} ===")
            
            # 一日分の胞子数をSENSORSに追加する
            for column in range(1, 6):
                SENSORS[column-1]["spore_count"] = int(row[column])
            
            # SENSORSの情報をprint
            print("--- Sensor Configurations ---")
            for s in SENSORS:
                print(f"Sensor {s['id']} [{s['name']}]: Location=({s['x']}, {s['y']}), Spore Count={s['spore_count']}")
            
            # この日の各組み合わせの誤差を格納するリスト
            day_errors = []
            
            # 全てのセンサの組み合わせで発生源推定を行う
            print("\n--- Estimation Results by Sensor Combinations ---")
            for comb in combinations:
                selected_sensors = [s for s in SENSORS if s["id"] in comb]
                comb_name = "-".join(comb)
                
                try:
                    est_x, est_y, total_c = estimate_source(selected_sensors)
                    error_distance = ((TRUE_SOURCE["x"] - est_x)**2 + (TRUE_SOURCE["y"] - est_y)**2)**0.5
                    print(f"Comb: {comb_name:<12} | Total Spore: {total_c:<3} | Est: ({est_x:.3f}, {est_y:.3f}) | Error: {error_distance:.3f}m")
                    day_errors.append(error_distance)
                    
                    #もしコマンドライン引数が--output-plotなら画像を保存する
                    if args.output_plot:
                        plot_simulation(
                            GREENHOUSE_WIDTH, 
                            GREENHOUSE_LENGTH, 
                            selected_sensors, 
                            est_x, 
                            est_y, 
                            TRUE_SOURCE["x"], 
                            TRUE_SOURCE["y"], 
                            save_path = "estimated_source/" + day + "/" + comb_name + ".png"
                        )
                except ValueError as e:
                    # 合計胞子数が0の場合は推定不可
                    print(f"Comb: {comb_name:<12} | Skip: {e}")
                    day_errors.append(None)
            
            # 結果を組み合わせ別に保存（この日の結果リストを二次元リストに追加）
            error_list.append(day_errors)

        
        #以下，誤差の距離を統計分析する
        print_error_table(days, combinations, error_list)
            
        #print("\nerror_list (raw data):")
        #print(*error_list, sep="\n")


if __name__ == "__main__":
    main()
