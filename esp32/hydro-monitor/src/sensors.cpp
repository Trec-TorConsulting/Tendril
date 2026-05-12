#include "sensors.h"
#include "config.h"
#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

static OneWire oneWire(ONEWIRE_PIN);
static DallasTemperature ds18b20(&oneWire);
static bool ds18b20Ok = false;

namespace tendril {

bool sensors_begin() {
    ds18b20.begin();
    ds18b20Ok = ds18b20.getDeviceCount() > 0;
    if (ds18b20Ok) {
        ds18b20.setResolution(12);
        Serial.printf("[sensors] DS18B20 OK (%d devices)\n", ds18b20.getDeviceCount());
    } else {
        Serial.println("[sensors] DS18B20 not found");
    }

    pinMode(PH_ADC_PIN, INPUT);
    pinMode(EC_ADC_PIN, INPUT);
    pinMode(ULTRA_TRIG_PIN, OUTPUT);
    pinMode(ULTRA_ECHO_PIN, INPUT);
    pinMode(MOSFET_PIN, OUTPUT);
    digitalWrite(MOSFET_PIN, LOW);

    Serial.println("[sensors] Hydro Monitor init complete");
    return ds18b20Ok;
}

static float readWaterTemp() {
    if (!ds18b20Ok) return -127.0f;
    ds18b20.requestTemperatures();
    float c = ds18b20.getTempCByIndex(0);
    if (c == DEVICE_DISCONNECTED_C) return -127.0f;
    return c;
}

static float readPH() {
    uint32_t sum = 0;
    for (int i = 0; i < 32; i++) {
        sum += analogRead(PH_ADC_PIN);
        delayMicroseconds(200);
    }
    float voltage = (float(sum) / 32.0f / 4095.0f) * 3.3f;
    float slope = (7.0f - 4.0f) / (PH_VOLTAGE_AT_7 - PH_VOLTAGE_AT_4);
    float ph = 7.0f + slope * (voltage - PH_VOLTAGE_AT_7);
    return constrain(ph, 0.0f, 14.0f);
}

static float readEC(float waterTempC) {
    uint32_t sum = 0;
    for (int i = 0; i < 32; i++) {
        sum += analogRead(EC_ADC_PIN);
        delayMicroseconds(200);
    }
    float voltage = (float(sum) / 32.0f / 4095.0f) * 3.3f;
    float ecRaw = voltage * EC_K_VALUE;
    float tempComp = 1.0f + EC_TEMP_COEFF * (waterTempC - 25.0f);
    return max(ecRaw / tempComp, 0.0f);
}

static float readDistance() {
    // JSN-SR04T ultrasonic ranging
    digitalWrite(ULTRA_TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(ULTRA_TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRA_TRIG_PIN, LOW);

    long duration = pulseIn(ULTRA_ECHO_PIN, HIGH, 30000);  // 30 ms timeout
    if (duration == 0) return -1.0f;

    // Speed of sound at ~25°C ≈ 346 m/s → 0.0346 cm/µs → distance = duration * 0.0173
    float cm = duration * 0.0173f;
    if (cm < 2.0f || cm > 500.0f) return -1.0f;
    return cm;
}

HydroReading sensors_read_hydro() {
    HydroReading r = {};

    // Power on 5V rail
    digitalWrite(MOSFET_PIN, HIGH);
    delay(PROBE_WARMUP_MS);

    // Water temperature
    float waterTempC = readWaterTemp();
    r.temp_valid = (waterTempC > -126.0f);
    if (r.temp_valid) {
        r.water_temp_f = roundf((waterTempC * 9.0f / 5.0f + 32.0f) * 10.0f) / 10.0f;
    }

    // pH
    r.ph = roundf(readPH() * 100.0f) / 100.0f;
    r.ph_valid = true;

    // EC (temperature compensated)
    float compTemp = r.temp_valid ? waterTempC : 25.0f;
    r.ec_ms = roundf(readEC(compTemp) * 100.0f) / 100.0f;
    r.ppm = (uint16_t)(r.ec_ms * 500.0f);
    r.ec_valid = true;

    // Water level
    float dist = readDistance();
    r.level_valid = (dist > 0);
    if (r.level_valid) {
        r.distance_cm = dist;
        float range = (float)(TANK_DEPTH_CM - TANK_FULL_CM);
        r.water_level_pct = constrain(100.0f * (TANK_DEPTH_CM - dist) / range, 0.0f, 100.0f);
        r.water_level_pct = roundf(r.water_level_pct * 10.0f) / 10.0f;
    }

    // Power off 5V rail
    digitalWrite(MOSFET_PIN, LOW);

    return r;
}

void hydro_to_json(const HydroReading& r, char* buf, size_t len) {
    JsonDocument doc;
    if (r.temp_valid)  doc["water_temp_f"]     = r.water_temp_f;
    if (r.ph_valid)    doc["ph"]               = r.ph;
    if (r.ec_valid) {
        doc["ec"]  = r.ec_ms;
        doc["ppm"] = r.ppm;
    }
    if (r.level_valid) {
        doc["water_level_pct"] = r.water_level_pct;
        doc["distance_cm"]     = r.distance_cm;
    }
    serializeJson(doc, buf, len);
}

} // namespace tendril
