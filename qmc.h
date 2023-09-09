/**
 * @file qmc.h
 * @author Italo C.J. Soares (italocjs@live.com)
 * @brief CODE IS FINE BUT ITS NOT WORKING DUO HARDWARE ISSUES! Setup and update
 * the API
 * @version 0.1
 * @date 2023-02-14
 * 2023-04-20 23:41:09 - Reviewed semaphores
 * 2023-04-25 19:02:34 - File upgraded for core 2.0, nothing changed but file location
 *
 * @copyright Copyright (c) 2023
 */

#pragma once
#include "core\api.h"
#include "program\config.h"

extern SemaphoreHandle_t xI2CSemaphore;

#include <QMC5883LCompass.h>

QMC5883LCompass compass;

void calibrate_compass()
{
	// Serial.begin(9600);
	compass.init();
	printf("This will provide calibration settings for your QMC5883L chip\r\n");
	printf("When prompted, move the magnetometer in all directions until the calibration is complete\r\n");

	delay(5000);
	printf("CALIBRATING. Keep moving your sensor...\r\n");
	compass.calibrate();

	float x_offset, y_offset, z_offset, x_scale, y_scale, z_scale;
	x_offset = compass.getCalibrationOffset(0);
	y_offset = compass.getCalibrationOffset(1);
	z_offset = compass.getCalibrationOffset(2);
	x_scale = compass.getCalibrationScale(0);
	y_scale = compass.getCalibrationScale(1);
	z_scale = compass.getCalibrationScale(2);

	printf("DONE: x_offset: %f, y_offset: %f, z_offset: %f, x_scale: %f, y_scale: %f, z_scale: %f\r\n", x_offset, y_offset, z_offset,
	       x_scale, y_scale, z_scale);
	compass.setCalibrationOffsets(x_offset, y_offset, z_offset);
	compass.setCalibrationScales(x_scale, y_scale, z_scale);
}

#include "soc/rtc_cntl_reg.h"
#include "soc/rtc_wdt.h"
#include "soc/soc.h"

int convertAzimuth(int azimuth) {
    if (azimuth < 0) {
        return azimuth + 360;
    }
    return azimuth;
}


TaskHandle_t Handle_taskQMC;
/**
 * @brief This task will update the API (day, month, year, hour, minute, second)
 * values every "UPDATE_CICLE_MS"
 */
void taskQMC5883L(void* pvParameters)
{
	ESP_LOGI("", "Task started");
	ESP_LOGE("", "Manetometer has started, but this is NOT working yet duo PCB issues");

	bool calibration_needed = false;
	if (calibration_needed)
	{
		bool semaphore_ok = false;
		while (!semaphore_ok)
		{
			semaphore_ok = (xSemaphoreTake(xI2CSemaphore, (TickType_t)(I2C_xBlockTime / portTICK_PERIOD_MS)) == pdTRUE);
			delay(10);
			ESP_LOGD("", "Waiting for semaphore to clear");
			if (semaphore_ok)
			{
				// rtc_wdt_feed();
				rtc_wdt_disable();    // Start the RTC WDT timer
				calibrate_compass();
				rtc_wdt_enable();    // Start the RTC WDT timer
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
			// compass.read();
			// // byte a = compass.getAzimuth();
			// // char myArray[3];
			// // compass.getDirection(myArray, a);
			// // Serial.print(myArray[0]);
			// // Serial.print(myArray[1]);
			// // Serial.print(myArray[2]);
			// // Serial.println();

			// // byte a = compass.getAzimuth();
			// int azimuth = compass.getAzimuth();
			// api.sensor_info.azimuth = azimuth;
			// Serial.print("Azimuth: ");
			// Serial.print(azimuth);
			// Serial.println();

			compass.read();
			int a = compass.getAzimuth();
			char myArray[3];
			compass.getDirection(myArray, a);

			printf("getDirection %c, %c, %c\t", myArray[0], myArray[1], myArray[2]);
			printf("Azimuth: %d", a);
			printf("\t Azimuth2: %d\r\n", convertAzimuth(a));

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
		ESP_LOGD("", "Waiting for semaphore to clear");
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

void qmc_testing_loop()
{
	if (xSemaphoreTake(xI2CSemaphore, (TickType_t)(I2C_xBlockTime / portTICK_PERIOD_MS)) == pdTRUE)
	{
		compass.read();

		byte a = compass.getAzimuth();

		char myArray[3];
		compass.getDirection(myArray, a);

		Serial.print(myArray[0]);
		Serial.print(myArray[1]);
		Serial.print(myArray[2]);
		Serial.println();
		xSemaphoreGive(xI2CSemaphore);    // Now free or "Give" the Serial Port for others.
	}
}