#ifndef SENSORS_H
#define SENSORS_H

#include <stdbool.h>

// Initialize I2C bus and BME680 sensor
// Returns true if BME680 was found on the bus
bool sensors_setup();

// Read all sensors and publish via MQTT
void sensors_read_and_publish();

#endif
