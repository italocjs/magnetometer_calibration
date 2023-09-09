/**
 * @brief Sample of how to send serial data for calibation
 * note: this file meant to run on pure C++, but can easily be integrated into an arduino or ESP32 project, just copy everything and replace the code if your actual functions (getX, getY, getZ, clearCalibration,millis,etc)
 */

#include <algorithm> //needed for sort
#include <cmath>
#include <cstdio> //needed for printf
#include <vector>

// Mock function to get x, make sure to replace with your actual function
long getX() { return rand() % 130001 - 65000; }
long getY() { return rand() % 130001 - 65000; }
long getZ() { return rand() % 130001 - 65000; }

void clearCalibration()
{
    // Your actual function to clear calibration
}

void csv_dump_example(int dump_duration_ms = 30000, bool samples_instead_of_duration = false)
{
    clearCalibration();
    unsigned long start_time = 0; // Replace with your time function, example startTime = millis();
    unsigned long current_time = 0; 
    printf("starting csv dump, move the device around all axis for at least 30 seconds, copy the x,y,z + all lines until the end\n");
    printf("\n\n\nx,y,z\n"); // csv start
    while ((current_time - start_time) < dump_duration_ms)
    { // Replace with your time function, example while((millis() - start_time) < test_duration_ms)
        long x = getX();
        long y = getY();
        long z = getZ();
        printf("%ld,%ld,%ld\n", x, y, z); // csv data
        if (samples_instead_of_duration)
            current_time++; // Use this if using an system without time function, or if you want to get an amount of samples instead of a
                            // duration
    }
    printf("\n\n\nend of csv dump - copy until last x,y,z values\n\n\n");
}

void apply_offset_correction(std::vector<long>& x, std::vector<long>& y, std::vector<long>& z, long& offset_x, long& offset_y,
                             long& offset_z)
{
	offset_x = (*std::max_element(x.begin(), x.end()) + *std::min_element(x.begin(), x.end())) / 2;
	offset_y = (*std::max_element(y.begin(), y.end()) + *std::min_element(y.begin(), y.end())) / 2;
	offset_z = (*std::max_element(z.begin(), z.end()) + *std::min_element(z.begin(), z.end())) / 2;

	for (size_t i = 0; i < x.size(); ++i)
	{
		x[i] -= offset_x;
		y[i] -= offset_y;
		z[i] -= offset_z;
	}
}

void apply_scale_correction(std::vector<long>& x, std::vector<long>& y, std::vector<long>& z,
                            float& scale_x, float& scale_y, float& scale_z)
{
	long avg_delta_x = (*std::max_element(x.begin(), x.end()) - *std::min_element(x.begin(), x.end())) / 2;
	long avg_delta_y = (*std::max_element(y.begin(), y.end()) - *std::min_element(y.begin(), y.end())) / 2;
	long avg_delta_z = (*std::max_element(z.begin(), z.end()) - *std::min_element(z.begin(), z.end())) / 2;
	long avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3;
	scale_x = (float)avg_delta / avg_delta_x;
	scale_y = (float)avg_delta / avg_delta_y;
	scale_z = (float)avg_delta / avg_delta_z;
	for (size_t i = 0; i < x.size(); ++i)
	{
		x[i] *= scale_x;
		y[i] *= scale_y;
		z[i] *= scale_z;
	}
}

void calibrate_example(int test_duration_ms = 30000, bool samples_instead_of_duration = false)
{
    clearCalibration();
    std::vector<long> x_values, y_values, z_values;

    unsigned long start_time = 0; // Replace with your time function, example startTime = millis();
    unsigned long current_time = 0;
    printf("starting calibration, move the device around all axis for at least 30 seconds\n");
    while ((current_time - start_time) < test_duration_ms)
    { // Replace with your time function, example while((millis() - start_time) < test_duration_ms)
        long x = getX();
        long y = getY();
        long z = getZ();
        x_values.push_back(x);
        y_values.push_back(y);
        z_values.push_back(z);
        if (samples_instead_of_duration)
            current_time++; // Use this if using an system without time function, or if you want to get an amount of samples instead of a
                            // duration
    }

    long offset_x, offset_y, offset_z;
	float scale_x, scale_y, scale_z;
	apply_offset_correction(x_values, y_values, z_values, offset_x, offset_y, offset_z);
	apply_scale_correction(x_values, y_values, z_values, scale_x, scale_y, scale_z);
	printf("Calibration values:\n");
	printf("\tValid samples: %d\n", x_values.size());
	printf("\tOffset: %ld, %ld, %ld\n", offset_x, offset_y, offset_z);
	printf("\tScale: %f, %f, %f\n", scale_x, scale_y, scale_z);
}

int main()
{
    csv_dump_example(500, true);
    calibrate_example(500, true);
    return 1;
}