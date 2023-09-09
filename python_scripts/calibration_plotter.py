import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

outlier_percentage = 0.02 # 0.02 recommended for better results, we should remove the outliers from this data, to reduce effect on the calibration

def plot_data(df, title, xlabel, ylabel):
    plt.figure(figsize=(10, 8))
    plt.scatter(df.iloc[:, 0], df.iloc[:, 1], s=10, label='XY', color='red')
    plt.scatter(df.iloc[:, 0], df.iloc[:, 2], s=10, label='XZ', color='green')
    plt.scatter(df.iloc[:, 1], df.iloc[:, 2], s=10, label='YZ', color='blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show(block=False)

def apply_offset_correction(df):
    offset_x = (max(df['x']) + min(df['x'])) / 2
    offset_y = (max(df['y']) + min(df['y'])) / 2
    offset_z = (max(df['z']) + min(df['z'])) / 2
    corrected_df = pd.DataFrame({
        'corrected_x': df['x'] - offset_x,
        'corrected_y': df['y'] - offset_y,
        'corrected_z': df['z'] - offset_z
    })
    return offset_x, offset_y, offset_z, corrected_df

def apply_scale_correction(df):
    avg_delta_x = (max(df['corrected_x']) - min(df['corrected_x'])) / 2
    avg_delta_y = (max(df['corrected_y']) - min(df['corrected_y'])) / 2
    avg_delta_z = (max(df['corrected_z']) - min(df['corrected_z'])) / 2
    avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3
    scale_x = avg_delta / avg_delta_x
    scale_y = avg_delta / avg_delta_y
    scale_z = avg_delta / avg_delta_z
    scaled_corrected_df = pd.DataFrame({
        'scaled_corrected_x': df['corrected_x'] * scale_x,
        'scaled_corrected_y': df['corrected_y'] * scale_y,
        'scaled_corrected_z': df['corrected_z'] * scale_z
    })
    return scale_x, scale_y, scale_z, scaled_corrected_df


def plot_comparison(original_df, comparated_df):
    s_size = 2
    plt.figure(figsize=(12, 10))
    plt.scatter(original_df['x'], original_df['y'], s=s_size, label='Original XY', color='lightblue', alpha=0.7)
    plt.scatter(original_df['x'], original_df['z'], s=s_size, label='Original XZ', color='skyblue', alpha=0.7)
    plt.scatter(original_df['y'], original_df['z'], s=s_size, label='Original YZ', color='deepskyblue', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_x'], comparated_df['scaled_corrected_y'], s=s_size, label='Calibrated XY', color='lightcoral', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_x'], comparated_df['scaled_corrected_z'], s=s_size, label='Calibrated XZ', color='hotpink', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_y'], comparated_df['scaled_corrected_z'], s=s_size, label='Calibrated YZ', color='orchid', alpha=0.7)
    plt.title("Comparison of Original and Fully Calibrated Plots")
    plt.xlabel("Original or Scaled and Corrected X or Y")
    plt.ylabel("Original or Scaled and Corrected Y or Z")
    plt.legend()
    plt.show(block=False)

def load_and_filter_csv(file_path, outlier_percentile=0.05):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    start_line = 0
    end_line = len(lines)
    
    # for i, line in enumerate(lines):
    #     if "CALIBRATING. Keep moving your sensor..." in line:
    #         start_line = i + 1  # Data starts after this line
    #     elif "DONE: x_offset:" in line:
    #         end_line = i  # Data ends before this line
    #         break
    
    # Filter lines and verify each line
    filtered_lines = []
    for line in lines[start_line:end_line]:
        if len(line.split(',')) == 3:  # Verify if the line contains exactly three parameters (x, y, z)
            filtered_lines.append(line)
    
    # Create a DataFrame from the filtered lines
    df = pd.read_csv(StringIO(''.join(filtered_lines)))
    
    # Filter out the top 5% and bottom 5% values in each column to remove noise
    for column in ['x', 'y', 'z']:
        lower_bound = df[column].quantile(0 + outlier_percentile/2)
        upper_bound = df[column].quantile(1 - outlier_percentile/2)
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    return df

def main():
    # Step 1: Read data from "data.csv"
    filtered_df = load_and_filter_csv("data.csv", outlier_percentage)
    
     #print how many lines are present in df
    print(f"Samples considered: {len(filtered_df)}, Noise removed percentage: {outlier_percentage}")

    # Step 2: Plot the original data
    # plot_data(df, title="Original Data", xlabel="X or Y", ylabel="Y or Z")
    
    # Step 3: Apply offset correction and plot the data
    offset_x, offset_y, offset_z, filtered_offset_df = apply_offset_correction(filtered_df)
    print(f"offset values ({offset_x},{offset_y},{offset_z})")
    # plot_data(df_offset, title="Offset Corrected Data", xlabel="Corrected X or Y", ylabel="Corrected Y or Z")
    
    # Step 4: Apply scale correction and plot the data
    scale_x, scale_y, scale_z, filtered_offset_scale_df = apply_scale_correction(filtered_offset_df)
    print(f"scale values ({scale_x},{scale_y},{scale_z})")
    # plot_data(df_offset_scale, title="Offset + Scale Corrected Data", xlabel="Scaled and Corrected X or Y", ylabel="Scaled and Corrected Y or Z")

    # Step 5: Show a comparison of the original and calibrated plots. make sure the calibrated plot is centered around 0.
    small_df = filtered_df.sample(frac=0.1) #better to plot 10% of the data for speed
    small_df_offset_scale = filtered_offset_scale_df.sample(frac=0.1) #better to plot 10% of the data for speed
    plot_comparison(small_df, small_df_offset_scale)

if __name__ == "__main__":
    main()

plt.show()
