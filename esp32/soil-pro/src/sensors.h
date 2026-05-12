#pragma once
#include <ArduinoJson.h>

namespace tendril {

struct SoilReading {
    int moisture_pct;
    float soil_temp_f;
    bool temp_valid;
    bool valid;
};

struct RunoffReading {
    float ph;
    float ec_ms;        // mS/cm
    uint16_t ppm;       // TDS (EC × 500)
    bool valid;
};

struct AmbientReading {
    float temp_f;
    float humidity;
    float pressure_hpa;
    float gas_kohms;
    bool valid;
};

bool sensors_begin();
SoilReading sensors_read_soil();
RunoffReading sensors_read_runoff(float solution_temp_c);
AmbientReading sensors_read_ambient();

void soil_to_json(const SoilReading& r, char* buf, size_t len);
void runoff_to_json(const RunoffReading& r, char* buf, size_t len);
void ambient_to_json(const AmbientReading& r, char* buf, size_t len);

} // namespace tendril
