#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct ZoneReading {
    uint8_t zone;           // 1-4
    int moisture_pct;
    float soil_temp_f;
    bool temp_valid;
};

struct AmbientReading {
    float temp_f;
    float humidity;
    float pressure_hpa;
    float gas_kohms;
    bool valid;
};

bool sensors_begin();
void sensors_read_zones(ZoneReading zones[], int count);
AmbientReading sensors_read_ambient();
void zones_to_json(const ZoneReading zones[], int count, char* buf, size_t len);
void ambient_to_json(const AmbientReading& r, char* buf, size_t len);

} // namespace tendril
