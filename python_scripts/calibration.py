import pandas as pd
from io import StringIO

outlier_percentage = 0.02 # 0.2 recommended for better results, we should remove the outliers from this data, to reduce effect on the calibration

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

# Function to filter the CSV and remove outliers
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

    # Step 3: Apply offset correction and plot the data
    offset_x, offset_y, offset_z, filtered_offset_df = apply_offset_correction(filtered_df)
    print(f"offset values ({offset_x},{offset_y},{offset_z})")
    
    # Step 4: Apply scale correction and plot the data
    scale_x, scale_y, scale_z, filtered_offset_scale_df = apply_scale_correction(filtered_offset_df)
    print(f"scale values ({scale_x},{scale_y},{scale_z})")

if __name__ == "__main__":
    main()
