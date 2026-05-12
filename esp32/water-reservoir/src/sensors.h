#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct ReservoirReading {
    float water_level_cm;
    int   water_level_pct;
    float water_temp_f;
    float flow_lpm;         // litres per minute
    float total_litres;     // cumulative (resets on power loss)
    bool  level_valid;
    bool  temp_valid;
    bool  flow_valid;
};

bool sensors_begin();
ReservoirReading sensors_read_all();
void reservoir_to_json(const ReservoirReading& r, char* buf, size_t len);

} // namespace tendril
