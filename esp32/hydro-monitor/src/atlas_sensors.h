#pragma once
/**
 * Atlas Scientific EZO I2C sensor driver for Tendril Hydro Monitor.
 *
 * Supports: EZO pH (0x63), EZO EC (0x64), EZO RTD (0x66), EZO DO (0x61)
 * All circuits must be switched to I2C mode before use.
 *
 * Usage:
 *   #define USE_ATLAS_SENSORS  // in config.h
 *   #include "atlas_sensors.h"
 */

#include <Wire.h>
#include <Arduino.h>

namespace tendril {
namespace atlas {

// Default I2C addresses (can be changed via EZO command)
constexpr uint8_t ADDR_DO  = 0x61;
constexpr uint8_t ADDR_ORP = 0x62;
constexpr uint8_t ADDR_PH  = 0x63;
constexpr uint8_t ADDR_EC  = 0x64;
constexpr uint8_t ADDR_RTD = 0x66;

// EZO response codes
constexpr uint8_t EZO_SUCCESS    = 1;
constexpr uint8_t EZO_FAIL       = 2;
constexpr uint8_t EZO_PENDING    = 254;
constexpr uint8_t EZO_NO_DATA    = 255;

struct AtlasReading {
    float ph;
    float ec_ms;       // mS/cm
    uint16_t ppm;      // 500 scale
    float water_temp_c;
    float water_temp_f;
    float do_mg_l;
    bool ph_valid;
    bool ec_valid;
    bool temp_valid;
    bool do_valid;
};

/**
 * Send a command string to an EZO circuit and read the response.
 * Returns the numeric value parsed from the response, or NAN on failure.
 */
inline float ezo_read(uint8_t address, const char* cmd = "R", uint16_t delay_ms = 900) {
    // Send command
    Wire.beginTransmission(address);
    Wire.print(cmd);
    Wire.endTransmission();

    delay(delay_ms);

    // Read response
    Wire.requestFrom(address, (uint8_t)20);
    if (!Wire.available()) return NAN;

    uint8_t code = Wire.read();
    if (code != EZO_SUCCESS) return NAN;

    char buf[20] = {};
    uint8_t i = 0;
    while (Wire.available() && i < sizeof(buf) - 1) {
        char c = Wire.read();
        if (c == 0) break;
        buf[i++] = c;
    }
    buf[i] = '\0';

    return atof(buf);
}

/**
 * Send a command without reading a value (e.g., calibration, temp compensation).
 * Returns true if EZO responds with success code.
 */
inline bool ezo_command(uint8_t address, const char* cmd, uint16_t delay_ms = 900) {
    Wire.beginTransmission(address);
    Wire.print(cmd);
    Wire.endTransmission();

    delay(delay_ms);

    Wire.requestFrom(address, (uint8_t)1);
    if (!Wire.available()) return false;
    return Wire.read() == EZO_SUCCESS;
}

/**
 * Check if an EZO circuit is present on the I2C bus.
 */
inline bool ezo_probe(uint8_t address) {
    Wire.beginTransmission(address);
    return Wire.endTransmission() == 0;
}

/**
 * Initialize the Atlas I2C bus and detect connected circuits.
 * Call from setup() after Wire.begin().
 */
inline void atlas_begin(int sda = 21, int scl = 22) {
    Wire.begin(sda, scl);
    Wire.setClock(100000);  // 100 kHz — EZO circuits prefer standard speed

    Serial.println("[atlas] Scanning I2C bus...");
    if (ezo_probe(ADDR_PH))  Serial.println("[atlas] pH  circuit found at 0x63");
    if (ezo_probe(ADDR_EC))  Serial.println("[atlas] EC  circuit found at 0x64");
    if (ezo_probe(ADDR_RTD)) Serial.println("[atlas] RTD circuit found at 0x66");
    if (ezo_probe(ADDR_DO))  Serial.println("[atlas] DO  circuit found at 0x61");
}

/**
 * Read all connected Atlas sensors.
 * Automatically applies temperature compensation to pH and EC if RTD is available.
 */
inline AtlasReading atlas_read_all() {
    AtlasReading r = {};

    // 1. Temperature first (needed for compensation)
    if (ezo_probe(ADDR_RTD)) {
        float temp_c = ezo_read(ADDR_RTD, "R", 600);
        if (!isnan(temp_c) && temp_c > -50.0f && temp_c < 150.0f) {
            r.water_temp_c = temp_c;
            r.water_temp_f = roundf((temp_c * 9.0f / 5.0f + 32.0f) * 10.0f) / 10.0f;
            r.temp_valid = true;

            // Send temperature compensation to pH and EC
            char comp[16];
            snprintf(comp, sizeof(comp), "T,%.1f", temp_c);
            if (ezo_probe(ADDR_PH)) ezo_command(ADDR_PH, comp, 300);
            if (ezo_probe(ADDR_EC)) ezo_command(ADDR_EC, comp, 300);
        }
    }

    // 2. pH
    if (ezo_probe(ADDR_PH)) {
        float ph = ezo_read(ADDR_PH, "R", 900);
        if (!isnan(ph) && ph >= 0.0f && ph <= 14.0f) {
            r.ph = roundf(ph * 100.0f) / 100.0f;
            r.ph_valid = true;
        }
    }

    // 3. EC
    if (ezo_probe(ADDR_EC)) {
        float ec_us = ezo_read(ADDR_EC, "R", 600);
        if (!isnan(ec_us) && ec_us >= 0.0f) {
            r.ec_ms = roundf((ec_us / 1000.0f) * 100.0f) / 100.0f;
            r.ppm = (uint16_t)(ec_us * 0.5f);  // 500 scale
            r.ec_valid = true;
        }
    }

    // 4. Dissolved Oxygen (optional)
    if (ezo_probe(ADDR_DO)) {
        float do_val = ezo_read(ADDR_DO, "R", 600);
        if (!isnan(do_val) && do_val >= 0.0f) {
            r.do_mg_l = roundf(do_val * 100.0f) / 100.0f;
            r.do_valid = true;
        }
    }

    return r;
}

/**
 * Serialize Atlas reading to JSON matching Tendril's MQTT payload format.
 */
inline void atlas_to_json(const AtlasReading& r, char* buf, size_t len) {
    // Manual JSON to avoid ArduinoJson dependency in header
    int written = snprintf(buf, len, "{");
    if (r.temp_valid)
        written += snprintf(buf + written, len - written, "\"water_temp_f\":%.1f,", r.water_temp_f);
    if (r.ph_valid)
        written += snprintf(buf + written, len - written, "\"ph\":%.2f,", r.ph);
    if (r.ec_valid) {
        written += snprintf(buf + written, len - written, "\"ec\":%.2f,", r.ec_ms);
        written += snprintf(buf + written, len - written, "\"ppm\":%u,", r.ppm);
    }
    if (r.do_valid)
        written += snprintf(buf + written, len - written, "\"do_mg_l\":%.2f,", r.do_mg_l);

    // Remove trailing comma and close
    if (buf[written - 1] == ',') written--;
    snprintf(buf + written, len - written, "}");
}

}  // namespace atlas
}  // namespace tendril
