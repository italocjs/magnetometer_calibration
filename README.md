# 🧭 Magnetometer Calibration: A Comprehensive Guide


## Introduction

Magnetometers are crucial for various applications like drones 🛸, robotics 🤖, and navigation systems 🗺️. However, they often suffer from inaccuracies due to various factors such as nearby electronic components, metal surfaces, and external magnetic fields. This article aims to provide a comprehensive guide on magnetometer calibration using Python, based on the GitHub repository [Magnetometer Calibration with Python and examples for ESP32 / Arduino](https://github.com/italocjs/magnetometer_calibration).

Example of common issues that can be fixed by calibration:
- Only pointing to one direction (ex north)
- Unable to "find" full 360 range
- Reading are unstable, you rotate the device n degrees but the read change is much higher or lower than expected


## 🛠️ Tools You'll Need
1. **Python**: Essential for data analysis and plotting. Python is the backbone of this calibration process, providing the necessary libraries and environment for data manipulation and visualization.
2. **Pandas**: A powerful library for data manipulation in Python. It offers data structures for efficiently storing large volumes of data and time-series functionality that allows you to slice, index, and subset large datasets.
3. **Matplotlib**: OPTIONAL but highly recommended for data visualization. It provides a way to plot a wide range of static, animated, and interactive visualizations in Python.
4. **C++/IDE**: If you're using an ESP32, you'll need to build the firmware. For this project testing i've chosen the ESP32 is a low-cost, low-power system on a chip (SoC) with Wi-Fi and Bluetooth capabilities, perfect for IoT projects.
5. **Magnetometer**: The example uses QMC5883L, but you can adapt it for any model. Magnetometers are devices that measure magnetic fields. They are commonly used in smartphones and other gadgets for determining the device's orientation relative to the Earth's magnetic field.


## Understanding the Calibration with Python 🐍
There are two Python scripts available to help you proccess the data, the only difference is that one also plots the image.

The Python script [`calibration_plotter.py`](https://github.com/italocjs/magnetometer_calibration/blob/main/python_scripts/calibration_plotter.py) is the recommended way to calibrate your device, ideally you should look at the plots and see if the final output is centered around zero and have similar shapes (must be circles).  If they are not. adjust the outlier percentage and try again. 


### Configuration Parameters

The script contains a few configuration parameters that you can adjust according to your needs:

```python
my_top_percentile = 0.025 #By default, the top and bottom 2.5% of data points are considered outliers and are removed from the dataset.
my_bottom_percentile = 0.025
save_plots_to_file = True # If set to True, the plots will be saved as png in the source folder
plot_sampling_percentage = 0.2 #helps reduce computational load for large datasets
figure_size = (10, 10) #size in inches
```
### Understanding the calibration and the plot images

One of the most useful features of the `calibration_plotter.py` script is its ability to generate visualizations that help in understanding the calibration process. These plots serve as a graphical representation of the data at various stages of calibration.

The script does the following steps:
1. **Read the data**: From a `.csv` file that you will paste your data.
    ```python
    original_df = load_clean_csv("python_scripts\data.csv")        
    ```
    - **Figure 1 - Data with outliers:** This plot shows the initial data with outliers. It helps in understanding the noise and inconsistencies in the raw magnetometer readings.
    <div style="text-align: center;"> <img src="https://github.com/italocjs/magnetometer_calibration/raw/main/Figure%201%20-%20Data%20with%20outliers.png" alt="drawing" width="600"/>
    </div>
    In an ideal sensor all data points would be in an evenly distributed circle centered around zero, but in reality, the data is often noisy and suffer from interference. This is where calibration comes in. It helps to counteract these errors, keep in mind that if your device is placed near any magnetic field during operation this will affect the readings. 


2. **Remove outliers**: one of the most important steps, makes sure that we filter out noise that would affect calibration.
    ```python
    filtered_df = filter_outlier(original_df, 0.025, 0.025)
    ```
    - **Figure 2 - Data without outliers**: After filtering out the outliers, this plot shows the cleaned data. It serves as a basis for further calibration steps. 
    <div style="text-align: center;"> <img src="https://github.com/italocjs/magnetometer_calibration/raw/main/Figure%202%20-%20Data%20without%20outliers.png" alt="drawing" width="600"/> </div>
     Removing the outliers has lowered out max and min values to something more reasonable, but the data is still not centered around zero, this is where offset correction comes in.

3. **Offset Correction**: Correcting the bias in the magnetometer readings.
    ```python
    offset_x, offset_y, offset_z, filtered_offset_df = apply_offset_correction(filtered_df)
    ```
    
    - **Figure 3 - Clean data and offset**: This plot shows the data after applying offset correction. The offset correction is crucial for aligning the data to the origin. 
    <div style="text-align: center;"> <img src="https://github.com/italocjs/magnetometer_calibration/raw/main/Figure%203%20-%20Clean%20data%20and%20offset.png" alt="drawing" width="600"/> </div>
    The offset correction has centered the data around zero, but the data is still not in a perfect circle, this is where scale correction comes in.

4. **Scale Correction**: Normalizing the readings to fall within a specific range.
    ```python
    scale_x, scale_y, scale_z, filtered_offset_scale_df = apply_scale_correction(filtered_offset_df)
    ```
    - **Figure 4 - Clean data offset and scale**: After applying both offset and scale corrections, this plot shows the calibrated data. It is the most accurate representation of the magnetic field.
    <div style="text-align: center;"> <img src="https://github.com/italocjs/magnetometer_calibration/raw/main/Figure%204%20-%20Clean%20data%20offset%20and%20scale.png" alt="drawing" width="600"/> </div>
    The scale correction has normalized the data to fall within an shared range. This is the final step in the calibration process and here you can see how much the data has improved, the new corrected plot must be centered around zero, and have similar shapes.

5. **Compare the result**: 
    - **Figure 5 - Comparison original vs calibrated**: This plot compares the original and calibrated data, highlighting the effectiveness of the calibration process.
    <div style="text-align: center;"> <img src="https://github.com/italocjs/magnetometer_calibration/raw/main/Figure%205%20-%20Comparison%20original%20vs%20calibrated.png" alt="drawing" width="600"/> </div>
    The blue-ish points are the original data, and the red-ish points are the calibrated ones. Above, you can see how the data improves post-calibration.

5. **Output the calibration values**: Python output:
    ```python
    [Running] python -u "c:\Users\italo\OneDrive\personal_python_projects\magnetometer_calibration\python_scripts\calibration_plotter.py"
    Total samples:  29573		outliers filtered: 2033/0.05%
    offset values X 1096	Y 3388	Z 2594 	xyz(1096,3388,2594)
    scale values X 1.020520	Y 1.017735	Z 0.963824 	xyz(1.020520,1.017735,0.96
    ```


## 🔄 C++ Implementation for ESP32
The ESP32 is a popular choice for IoT projects due to its low cost, low power consumption, and built-in Wi-Fi and Bluetooth capabilities. It's a versatile platform that can easily integrate with various sensors, including magnetometers.

While the Python script provides a comprehensive solution for magnetometer calibration on a computer, there might be scenarios where you'd want to apply these calibrations directly on a microcontroller like the ESP32. The GitHub repository also includes a C++ sample implementation for this purpose.  Please be aware that this method will not supports several thousands of data points, from my testing the max i was able to get was ~300 on ESP32 which did produced good enough results, increasing task stack did not help.

1. **Compatibility**: The code is compatible with the QMC5883L magnetometer but can be easily adapted for other models.

2. **Efficiency**: This code is has not been specifically optimized for efficiency in embedded environments, some environments might not support all c++ features used.

### Final Thoughts

Whether you are a hobbyist working on a DIY project or a professional developing a commercial product, understanding the nuances of magnetometer calibration can go a long way in ensuring the success of your project.

Thank you for reading this guide on magnetometer calibration. i hope you found it informative and useful. For more details, you can visit the [GitHub repository](https://github.com/italocjs/magnetometer_calibration).

Happy calibrating! 🧲🛠️