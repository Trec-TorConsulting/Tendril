#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct AeroReading {
    float water_temp_f;
    float ph;
    float ec_ms;
    uint16_t ppm;
    float water_level_pct;
    float mist_pressure_psi;
    bool temp_valid;
    bool level_valid;
    bool pressure_valid;
};

bool sensors_begin();
AeroReading sensors_read_all();
void aero_to_json(const AeroReading& r, char* buf, size_t len);

} // namespace tendril
