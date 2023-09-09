# 🧭 Magnetometer Calibration with Python and examples for ESP32 / Arduino
## Introduction
Have you ever suffered with the weird behavior of magnetometers like the QMC5883L and HMC5883, not pointing to anywhere, innacurate readings and values that make no sense? these examples will help you apply some calibration techniques and script to dramatically improve your magnetometer's precision and reliability. 🎯

## 🤔 Why does it needs to be calibrated?

Magnetometers are sensitive devices. They can be influenced by nearby chip and components, nearby metal surfaces, external magnetic fields, temperature, the orientation of the device. These innacuracies can sum up to deliver unusable sensor readings (example, an sensor that only poins to north or not reaching full 360 angle) This is critical for applications like drones 🛸, robotics 🤖, or any other navigation systems 🗺️. Calibration helps to counteract these errors, but keep in mind that if your device is placed near any magnetic field during operation this will affect the readings.  

![Original vs Calibrated Data](https://github.com/italocjs/magnetometer_calibration/blob/b9ea9760c468e9c752ac4942b83872dba0c7d772/Figure_4.png)  
*Above, you can see how the data improves post-calibration. The blue points are the original data, and the red points are the calibrated ones.*

## 🛠️ Tools You'll Need

1. **Python**: For data analysis and plotting.
4. **Pandas**: For data manipulation.
3. **Matplotlib**: OPTIONAL: For data visualization.
2. **C++/IDE**: If you're using an ESP32, you'll need this for firmware.
5. **Magnetometer**: We're using QMC5883L, but with a few tweaks, you can adapt this for any model.

### Python Script 🐍
Therea are two Python scripts to help you proccess the "csv" data that is sent to terminal. both uses Pandas for data manipulation and calibration
but there is one special with Matplotlib for plotting

1. **Reading Data**: From a `.csv` file that you will paste your data.
2. **Outlier removal**: one of the most important steps, makes sure that we filter out noise that would affect calibration.
3. **Offset Correction**: Correcting the bias in the magnetometer readings.
4. **Scale Correction**: Normalizing the readings to fall within a specific range.
5. **Plot data comparison**: Plotting the corrected data for evaluation.

![Final Calibrated Data](placeholder_image_url_2.png)

### C++ sample implementation for ESP32 🛠️
The recommended way to calibrate is by logging all the sensor data and processing it with python. with the tool you will receive better results
than with embededed processing, you will also be able to visually check if the calibration is good.

1. **Collect Data**: use csv_dump_example() to help you acquire data, modify it to your actual functions
2. **Run Python Script**: Feed this data into the Python script.
3. **Analyze Plots**: Observe the initial and final plots to understand how much the data has improved, the new corrected plot must be centered around zero, and have similar shapes.
4. **Apply Corrections**: Use the calculated offset and scale values in your C++ code for correction.

There is also an example of how to implement the calibration inside the microcontroller, it uses the same concept but supports less data points
*note: max data points with esp32 was 300, increasing task stack did not help.