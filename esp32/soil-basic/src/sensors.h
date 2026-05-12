#pragma once
/// @file sensors.h
/// Soil Basic sensor interface — capacitive soil moisture + BME680 ambient.

#include <ArduinoJson.h>

namespace tendril {

struct SoilReading {
    int moisture_pct;       // 0-100
    int raw_adc;            // Raw ADC value for diagnostics
    bool valid;
};

struct AmbientReading {
    float temp_f;           // Fahrenheit
    float humidity;         // %RH
    float pressure_hpa;     // hPa
    float gas_kohms;        // kΩ (VOC indicator)
    bool valid;
};

/// Initialise I2C and ADC.  Returns true if BME680 was found.
bool sensors_begin();

/// Read the capacitive soil moisture sensor.
SoilReading sensors_read_soil();

/// Read the BME680 ambient sensor.  Returns invalid if BME680 not present.
AmbientReading sensors_read_ambient();

/// Serialise soil reading to JSON.  Caller provides the buffer.
void soil_to_json(const SoilReading& r, char* buf, size_t len);

/// Serialise ambient reading to JSON.
void ambient_to_json(const AmbientReading& r, char* buf, size_t len);

} // namespace tendril
