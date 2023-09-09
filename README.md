# 🧭 Magnetometer Calibration with Python and examples for ESP32 / Arduino
## Introduction
Hey there, programmers, firmware devs, drone enthusiasts, and hardware engineers! 🛠️ Have you ever suffered with the weird behavior of new magnetometers like the QMC5883L and HMC5883? this article is your compass to navigate through the calibration techniques and script to dramatically improve your magnetometer's precision and reliability. 🎯

## 🤔 Why Calibration?

Magnetometers are sensitive devices. They can be influenced by nearby chip and components, nearby metal surfaces, external magnetic fields, temperature, the orientation of the device. These innacuracies can sum up to deliver unusable sensor readings (example, an sensor that only poins to north or not reaching full 360 angle) This is critical for applications like drones 🛸, robotics 🤖, or any other navigation systems 🗺️. Calibration helps to counteract these errors, but keep in mind that if your device is placed near any magnetic field during operation this will affect the readings.

![Original vs Calibrated Data](https://github.com/italocjs/magnetometer_calibration/blob/b9ea9760c468e9c752ac4942b83872dba0c7d772/Figure_4.png)  
*Above, you can see how the data improves post-calibration. The blue points are the original data, and the red points are the calibrated ones.*

## 🛠️ Tools You'll Need

1. **Python**: For data analysis and plotting.
2. **C++**: If you're using an ESP32, you'll need this for firmware.
3. **Matplotlib**: For data visualization.
4. **Pandas**: For data manipulation.
5. **Magnetometer**: We're using QMC5883L, but with a few tweaks, you can adapt this for any model.

## 💡 Platform Independence

The beauty of this code is its platform independence. You can adapt it to work with any magnetometer as long as you can modify the code to print the data. For example:

```cpp
printf("x,y,z\r\n"); //csv start
unsigned long startTime = millis();
while ((millis() - startTime) < 60000)
{
	x = getX(); // Modify this to your actual get_data_from_axis_function()
	y = getY(); 
	z = getZ();
	printf("%ld,%ld,%ld\r\n", x, y, z); //csv data
}
```

## 📚 Understanding the Code

The code comprises mainly two parts:

### Python Script 🐍
The Python script uses Pandas for data manipulation and Matplotlib for plotting. It's responsible for:

1. **Reading Data**: From a `.csv` file.
2. **Initial Plotting**: Of X, Y, Z magnetic fields.
3. **Offset Correction**: Correcting the bias in the magnetometer readings.
4. **Scale Correction**: Normalizing the readings to fall within a specific range.
5. **Final Plotting**: Plotting the corrected data for evaluation.

![Final Calibrated Data](placeholder_image_url_2.png)

### C++ sample implementation for ESP32 🛠️
The C++ code is your firmware that runs on the ESP32. It reads the data from the magnetometer and sends it to Python for further analysis.

## 🚀 How to Use the Code

1. **Collect Data**: Use your ESP32 to collect magnetometer data.
2. **Run Python Script**: Feed this data into the Python script.
3. **Analyze Plots**: Observe the initial and final plots to understand how much the data has improved.
4. **Apply Corrections**: Use the calculated offset and scale values in your C++ code for real-time correction.

```python
# Python snippet for offset correction
offset_x = (max(x) + min(x)) / 2
corrected_x = x - offset_x
```

```cpp
// C++ snippet for applying offset in real-time
float correctedX = rawX - offset_x;
```

## 📊 Visualizations Keep You on Track
The code uses Matplotlib to plot the data before and after calibration. This allows you to visually inspect the improvements. You can see plots for `XY`, `XZ`, and `YZ` planes, which are crucial for 3D space navigation.

## 🎯 What You'll Achieve
1. **Higher Precision**: More reliable readings.
2. **Better Navigation**: Essential for drones and robotics.
3. **Understanding of Calibration Techniques**: Useful for various sensors and applications.

## 📝 Final Thoughts
Calibration is not just an optional step; it's a necessity for precise and reliable magnetometer readings. This guide provides you with the tools and code to make that happen. So go ahead, calibrate your magnetometers and let your projects find their true north! 🧭

Happy Coding and Calibrating! 🎉
