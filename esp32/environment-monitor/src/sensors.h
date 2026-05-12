#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct EnvironmentReading {
    float temp_f;
    float humidity;
    float vpd_kpa;
    float dew_point_f;
    uint16_t co2_ppm;
    float lux;
    float pressure_hpa;
    float gas_kohms;
    bool bme_valid;
    bool co2_valid;
    bool lux_valid;
};

bool sensors_begin();
EnvironmentReading sensors_read_all();
void env_to_json(const EnvironmentReading& r, char* buf, size_t len);

} // namespace tendril
