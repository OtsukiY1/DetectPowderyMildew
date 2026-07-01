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

# Greenhouse Dimensions (default config)
GREENHOUSE_WIDTH = 6.28   # x-axis (meters)
GREENHOUSE_LENGTH = 10.01 # y-axis (meters)

# Default Sensor Layout and Spore Counts (C_i)
# Coordinates are in meters relative to the bottom-left corner of the house (0, 0)
DEFAULT_SENSORS = [
    {"id": "A", "name": "Bottom-Left (左下)", "x": 1.45, "y": 2.52, "spore_count": 14},
    {"id": "B", "name": "Top-Left (左上)", "x":1.45 , "y": GREENHOUSE_LENGTH - 2.36, "spore_count": 9},
    {"id": "C", "name": "Bottom-Right (右下)", "x": GREENHOUSE_WIDTH - 1.76, "y": 2.52, "spore_count": 8},
    {"id": "D", "name": "Top-Right (右上)", "x": GREENHOUSE_WIDTH - 1.76, "y": GREENHOUSE_LENGTH - 2.36, "spore_count": 12},
    {"id": "E", "name": "Center (真ん中)", "x":2.97, "y":5.68, "spore_count": 16},
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


def main():
    parser = argparse.ArgumentParser(description="Infection Source Estimation")
    parser.add_argument("--output-plot", type=str, default=None, help="Path to save the generated visualization plot")
    args = parser.parse_args()
    
    print("=== Powdery Mildew Infection Source Estimation (Centroid Method) ===")
    print(f"Greenhouse Dimensions: {GREENHOUSE_WIDTH}m (Width) x {GREENHOUSE_LENGTH}m (Length)")
    print(f"True Infection Source Coordinate: ({TRUE_SOURCE['x']}, {TRUE_SOURCE['y']})")
    print("\n--- Sensor Configurations ---")
    for s in DEFAULT_SENSORS:
        print(f"Sensor {s['id']} [{s['name']}]: Location=({s['x']}, {s['y']}), Spore Count={s['spore_count']}")
        
    try:
        est_x, est_y, total_c = estimate_source(DEFAULT_SENSORS)
        error_distance = ((TRUE_SOURCE["x"] - est_x)**2 + (TRUE_SOURCE["y"] - est_y)**2)**0.5
        
        print("\n--- Estimation Results ---")
        print(f"Total Spore Count: {total_c}")
        print(f"Estimated Infection Source Coordinate: ({est_x:.3f}, {est_y:.3f})")
        print(f"True Infection Source Coordinate: ({TRUE_SOURCE['x']:.3f}, {TRUE_SOURCE['y']:.3f})")
        print(f"Estimation Error Distance: {error_distance:.3f} meters")
        
        # Plot if requested
        if args.output_plot:
            plot_simulation(
                GREENHOUSE_WIDTH, 
                GREENHOUSE_LENGTH, 
                DEFAULT_SENSORS, 
                est_x, 
                est_y, 
                TRUE_SOURCE["x"], 
                TRUE_SOURCE["y"], 
                save_path=args.output_plot
            )
            
    except ValueError as e:
        print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
