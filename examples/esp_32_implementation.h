/**
 * @brief Sample of how to send serial data for calibation
 * note: this file has been tested with esp32.
 * Embedded calibration works, with esp32 tested up to 300 samples (this exact code),
 * it has crashed with 600 samples, increasing task stack size did not help.
 *
 * I highly recommend to use the csv_dump_example() function and process it using python, it will provide more accurate results and also
 * provide an plot image of the data, on which you can visually see if the calibration is good.
 */

// Requires freertos includes!, update for your port.  (arduino.h also includes it)
#include <QMC5883LCompass.h>

#include <algorithm>    //needed for sort
#include <cmath>
#include <cstdio>    //needed for printf
#include <vector>
QMC5883LCompass compass;

void csv_dump_example(int dump_duration_ms = 30000)
{
	compass.clearCalibration();
	unsigned long start_time = millis();
	printf("starting csv dump, move the device around all axis for at least 30 seconds, copy the x,y,z + all lines until the end\n");
	printf("\n\n\nx,y,z\n");    // csv start
	while ((millis() - start_time) < dump_duration_ms)
	{    // Replace with your time function, example while((millis() - start_time) < test_duration_ms)
		long x = compass.getX();
		long y = compass.getY();
		long z = compass.getZ();
		printf("%ld,%ld,%ld\n", x, y, z);    // csv data
		delay(1);                            // avoid serial crash and watchdog trigger
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

void apply_scale_correction(std::vector<long>& x, std::vector<long>& y, std::vector<long>& z, float& scale_x, float& scale_y,
                            float& scale_z)
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

void calibrate_example(int test_duration_ms = 30000, int sample_delay = 100)
{
	printf("starting calibration, move the device around all axis for at least 30 seconds\n");
	compass.clearCalibration();
	printf("expected array size: %d\n", test_duration_ms / sample_delay);
	std::vector<long> x_values, y_values, z_values;
	unsigned int start_time = millis();
	while ((millis() - start_time) < test_duration_ms)
	{
		compass.read();
		x_values.push_back(compass.getX());
		y_values.push_back(compass.getY());
		z_values.push_back(compass.getZ());
		delay(sample_delay);
		rtc_wdt_feed();    // if your code has wdt enabled, feed it here to avoid crash
	}
	// printf("DEBUG: array filled\n");
	// printf("DEBUG: array size: %d\n", x_values.size());
	// printf("DEBUG: array capacity: %d\n", x_values.capacity());
	// printf("DEBUG: array max_size: %d\n", x_values.max_size());
	// printf("DEBUG: x min: %d\n", *std::min_element(x_values.begin(), x_values.end()));
	// printf("DEBUG: x max: %d\n", *std::max_element(x_values.begin(), x_values.end()));
	// printf("DEBUG: y min: %d\n", *std::min_element(y_values.begin(), y_values.end()));
	// printf("DEBUG: y max: %d\n", *std::max_element(y_values.begin(), y_values.end()));
	// printf("DEBUG: z min: %d\n", *std::min_element(z_values.begin(), z_values.end()));
	// printf("DEBUG: z max: %d\n", *std::max_element(z_values.begin(), z_values.end()));
	// get_scale(x_values, y_values, z_values);

	long offset_x, offset_y, offset_z;
	float scale_x, scale_y, scale_z;
	apply_offset_correction(x_values, y_values, z_values, offset_x, offset_y, offset_z);
	apply_scale_correction(x_values, y_values, z_values, scale_x, scale_y, scale_z);
	printf("Calibration values:\n");
	printf("\tValid samples: %d\n", x_values.size());
	printf("\tOffset: %ld, %ld, %ld\n", offset_x, offset_y, offset_z);
	printf("\tScale: %f, %f, %f\n", scale_x, scale_y, scale_z);
	// print number of samples
	compass.setCalibrationOffsets(offset_x, offset_y, offset_z);
	compass.setCalibrationScales(scale_x, scale_y, scale_z);
	printf("Calibration has been set, but not saved to Preferences yet\n");
}

TaskHandle_t Handle_taskQMC;
/**
 * @brief This is a sample freeRTOS task that reads the compass and prints the values to the serial port.
 */
void taskQMC5883L(void* pvParameters)
{
	ESP_LOGI(QMC_TAG, "Task started");
	bool calibration_needed = true;
	if (calibration_needed)
	{
		bool semaphore_ok = false;
		while (!semaphore_ok)
		{
			semaphore_ok = (xSemaphoreTake(xI2CSemaphore, (TickType_t)(I2C_xBlockTime / portTICK_PERIOD_MS)) == pdTRUE);
			delay(10);
			ESP_LOGD(QMC_TAG, "Waiting for semaphore to clear");
			if (semaphore_ok)
			{
				csv_dump_example(); //This is the recommended way to calibrate the compass
				// calibrate_example(); 
				xSemaphoreGive(xI2CSemaphore);
			}
		}
	}
	else
	{
		compass.setCalibrationOffsets(1100.0, 3385.0, 2590.0);
		compass.setCalibrationScales(1.0295774647887324, 1.0152777777777777, 0.9580602883355177);
	}
	for (;;)
	{
		if (xSemaphoreTake(xI2CSemaphore, (TickType_t)(I2C_xBlockTime / portTICK_PERIOD_MS)) == pdTRUE)
		{
			compass.read();
			int azimuth = compass.getAzimuth();
			char myArray[3];
			compass.getDirection(myArray, azimuth);

			printf("getDirection %c, %c, %c", myArray[0], myArray[1], myArray[2]);
			printf("\tAzimuth: %d", azimuth);
			int azimuth360;

			if (azimuth < 0)
			{
				azimuth360 = azimuth + 360;
			}
			else
			{
				azimuth360 = azimuth;
			}
			printf("\tAzimuth 360: %d\r\n", azimuth360);

			xSemaphoreGive(xI2CSemaphore);
			vTaskDelay(1000 / portTICK_PERIOD_MS);
		}
		else
			vTaskDelay(I2C_RETRY_DELAY / portTICK_PERIOD_MS);
	}
}

void qmcsetup()
{
	bool semaphore_ok = false;
	while (!semaphore_ok)
	{
		semaphore_ok = (xSemaphoreTake(xI2CSemaphore, (TickType_t)(I2C_xBlockTime / portTICK_PERIOD_MS)) == pdTRUE);
		delay(10);
		ESP_LOGD(QMC_TAG, "Waiting for semaphore to clear");
	}

	if (semaphore_ok)
	{
		compass.init();
		xSemaphoreGive(xI2CSemaphore);
		xTaskCreatePinnedToCore(taskQMC5883L,       /* Task function. */
		                        "taskQMC5883L",     /* name of task. */
		                        DEFAULT_STACK_SIZE, /* Stack size of task */
		                        NULL,               /* parameter of the task */
		                        1,                  /* priority of the task */
		                        &Handle_taskQMC,    /* Task handle to keep track of created task */
		                        1);
	}
}