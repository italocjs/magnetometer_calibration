# Make sure to install pandas, numpy and matplotlib before running this script,  it should run automatically under jupyter notebook
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from io import StringIO

# Be sure to remove your outliers and check the data to see if it looks correct. ideally there should not any dots far from the "circles".
my_top_percentile = 0.025 # Percentage of outliers to remove from the top of the data, increase adjust until you data looks cleaned.
my_bottom_percentile = 0.025 # Percentage of outliers to remove from the bottom of the data
save_plots_to_file = True   # Set to True to save the plots to a file
plot_sampling_percentage = 0.2 # Adjust if need to plot faster, 1.0 = 100% of the data, 0.5 = 50% of the data, 0.1 = 10% of the data, etc.
figure_size = (10, 10) # Adjust the size of all the plots, (width, height)   

# Base functions for calibration
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

def load_clean_csv(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    start_line = 0
    end_line = len(lines)

    # Filter lines and verify each line
    filtered_lines = []
    for line in lines[start_line:end_line]:
        if len(line.split(',')) == 3:  # Verify if the line contains exactly three parameters (x, y, z)
            filtered_lines.append(line)
    
    # Create a DataFrame from the filtered lines
    df = pd.read_csv(StringIO(''.join(filtered_lines)))
    return df

def filter_outlier(df, top_percentile=my_top_percentile, bottom_percentile=my_bottom_percentile):
    # Filter out the top 5% and bottom 5% values in each column to remove noise
    for column in ['x', 'y', 'z']:
        lower_bound = df[column].quantile(0 + bottom_percentile/2)
        upper_bound = df[column].quantile(1 - top_percentile/2)
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

# Helper functions for plotting
def clean_filename(filename):
    # return filename.replace(' ', '_').replace('/', '_').replace('\\', '_').replace(':', '_')
    return filename.replace('/', '_').replace('\\', '_').replace(':', '_')

def calculate_distance_from_origin(x, y):
    return np.sqrt(x ** 2 + y ** 2)

def normalize(distances, min_val, max_val):
    min_dist, max_dist = np.min(distances), np.max(distances)
    return min_val + (max_val - min_val) * (distances - min_dist) / (max_dist - min_dist)

def plot_dist_from_origin(df, title, xlabel, ylabel, save_img=False):
    plt.figure(title,figsize=figure_size)

    # Create a custom colormap
    c_map = LinearSegmentedColormap.from_list('custom_cmap', ['cyan', 'red'], N=256)
    
    # Calculate distances for different combinations of coordinates
    distances_xy = calculate_distance_from_origin(df.iloc[:, 0], df.iloc[:, 1])
    distances_xz = calculate_distance_from_origin(df.iloc[:, 0], df.iloc[:, 2])
    distances_yz = calculate_distance_from_origin(df.iloc[:, 1], df.iloc[:, 2])
    
    # Normalize alpha values and color values based on distances
    alpha_xy = normalize(distances_xy, 0.1, 0.5)
    alpha_xz = normalize(distances_xz, 0.1, 0.5)
    alpha_yz = normalize(distances_yz, 0.1, 0.5)
    
    # Scatter plot using calculated distances for color and alpha
    plt.scatter(df.iloc[:, 0], df.iloc[:, 1], s=2, c=distances_xy, cmap=c_map, alpha=alpha_xy, label='XY')
    plt.scatter(df.iloc[:, 0], df.iloc[:, 2], s=2, c=distances_xz, cmap=c_map, alpha=alpha_xz, label='XZ')
    plt.scatter(df.iloc[:, 1], df.iloc[:, 2], s=2, c=distances_yz, cmap=c_map, alpha=alpha_yz, label='YZ')
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.colorbar(label='Distance from Origin')
    # Make the aspect ratio equal
    plt.axis('equal')

    if save_img:
        plt.savefig(f"{clean_filename(title)}.png")

    plt.show(block=False)

def plot_comparison(original_df, comparated_df, title,save_img=False):
    s_size = 2
    plt.figure(title,figsize=figure_size)
    plt.scatter(original_df['x'], original_df['y'], s=s_size, label='Original XY', color='lightblue', alpha=0.7)
    plt.scatter(original_df['x'], original_df['z'], s=s_size, label='Original XZ', color='skyblue', alpha=0.7)
    plt.scatter(original_df['y'], original_df['z'], s=s_size, label='Original YZ', color='deepskyblue', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_x'], comparated_df['scaled_corrected_y'], s=s_size, label='Comparated XY', color='lightcoral', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_x'], comparated_df['scaled_corrected_z'], s=s_size, label='Comparated XZ', color='hotpink', alpha=0.7)
    plt.scatter(comparated_df['scaled_corrected_y'], comparated_df['scaled_corrected_z'], s=s_size, label='Comparated YZ', color='orchid', alpha=0.7)
    plt.title(title)
    plt.xlabel("XY")
    plt.ylabel("YZ")
    plt.legend()
    # Make the aspect ratio equal
    plt.axis('equal')
    if save_img:
        plt.savefig(f"{clean_filename(title)}.png")

    plt.show(block=False)

def plot_data(df, title, xlabel, ylabel,save_img=False):
    plt.figure(title,figsize=figure_size)
    plt.scatter(df.iloc[:, 0], df.iloc[:, 1], s=2, label='XY', color='red')
    plt.scatter(df.iloc[:, 0], df.iloc[:, 2], s=2, label='XZ', color='green')
    plt.scatter(df.iloc[:, 1], df.iloc[:, 2], s=2, label='YZ', color='blue')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    # Make the aspect ratio equal
    plt.axis('equal')
    if save_img:
        plt.savefig(f"{clean_filename(title)}.png")
        
    plt.show(block=False)

# Main function
def main():
    # Step 1: Read data from "data.csv"
    original_df = load_clean_csv("python_scripts\data.csv") # helper function to load and clean the data, makes sure only lines with x,y,z values are present
    
    # Step 2: Filter out the outliers and print some information about the data
    filtered_df = filter_outlier(original_df, 0.025, 0.025)
    print(f"Total samples:  {len(original_df)}\t\toutliers filtered: {len(original_df) - len(filtered_df)}/{my_top_percentile + my_bottom_percentile}%")
    
    # Step 3: Apply offset correction and plot the data
    offset_x, offset_y, offset_z, filtered_offset_df = apply_offset_correction(filtered_df)
    print(f"offset values X {int(offset_x)}\tY {int(offset_y)}\tZ {int(offset_z)} \txyz({int(offset_x)},{int(offset_y)},{int(offset_z)})")
    
    # Step 4: Apply scale correction and plot the data
    scale_x, scale_y, scale_z, filtered_offset_scale_df = apply_scale_correction(filtered_offset_df)
    print(f"scale values X {scale_x:.6f}\tY {scale_y:.6f}\tZ {scale_z:.6f} \txyz({scale_x:.6f},{scale_y:.6f},{scale_z:.6f})")

    # Step 5: Plot some information about the original data
    # Tip: Sampling the data with outliers is not a good idea, as the outliers may are likely to be removed and not plotted, for the other plots, sampling is fine but not required
    plot_data(original_df, title="Figure 1 - Data with outliers", xlabel="XY", ylabel="YZ", save_img=save_plots_to_file)
    plot_dist_from_origin(original_df, title="Figure 1.1 - DistofOrigin of Data with outliers", xlabel="XY", ylabel="YZ", save_img=save_plots_to_file)

    # Step 7: Plot some information about the outlier cleaned data
    plot_data(filtered_df.sample(frac=plot_sampling_percentage), title="Figure 2 - Data without outliers", xlabel="XY", ylabel="YZ", save_img=save_plots_to_file)
    plot_dist_from_origin(filtered_df.sample(frac=plot_sampling_percentage), title="Figure 2.2 - DistofOrigin of Data without outliers", xlabel="XY", ylabel="YZ", save_img=save_plots_to_file)

    # Step 8: Plot some information about the offset corrected data
    plot_data(filtered_offset_df.sample(frac=plot_sampling_percentage), title="Figure 3 - Clean data and offset", xlabel="Offset corrected XY", ylabel="Offset corrected YZ", save_img=save_plots_to_file)
    plot_dist_from_origin(filtered_offset_df.sample(frac=plot_sampling_percentage), title="Figure 3.1 - DistofOrigin of Clean data and offset", xlabel="Offset corrected XY", ylabel="Offset corrected YZ", save_img=save_plots_to_file)

    # Step 9: Plot some information about the offset and scale corrected data
    plot_data(filtered_offset_scale_df.sample(frac=plot_sampling_percentage), title="Figure 4 - Clean data offset and scale", xlabel="Offset+Scale Corrected XY", ylabel="Offset+Scale Corrected YZ", save_img=save_plots_to_file)
    plot_dist_from_origin(filtered_offset_scale_df.sample(frac=plot_sampling_percentage), title="Figure 4.1 - DistofOrigin of Clean data offset and scale", xlabel="Offset+Scale Corrected XY", ylabel="Offset+Scale Corrected YZ", save_img=save_plots_to_file)

    # Step 5: Show a comparison of the original and calibrated plots. make sure the calibrated plot is centered around 0.
    plot_comparison(filtered_df.sample(frac=plot_sampling_percentage), filtered_offset_scale_df.sample(frac=plot_sampling_percentage),"Figure 5 - Comparison original vs calibrated",save_img=save_plots_to_file)

if __name__ == "__main__":
    main()

plt.show()
