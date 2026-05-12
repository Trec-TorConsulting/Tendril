#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct HydroReading {
    float water_temp_f;
    float ph;
    float ec_ms;
    uint16_t ppm;
    float water_level_pct;
    float distance_cm;
    bool temp_valid;
    bool ph_valid;
    bool ec_valid;
    bool level_valid;
};

bool sensors_begin();
HydroReading sensors_read_hydro();
void hydro_to_json(const HydroReading& r, char* buf, size_t len);

} // namespace tendril
