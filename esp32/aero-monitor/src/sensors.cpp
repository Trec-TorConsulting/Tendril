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
    if (ds18b20Ok) ds18b20.setResolution(12);

    pinMode(PH_ADC_PIN, INPUT);
    pinMode(EC_ADC_PIN, INPUT);
    pinMode(ULTRA_TRIG_PIN, OUTPUT);
    pinMode(ULTRA_ECHO_PIN, INPUT);
    pinMode(PRESSURE_ADC_PIN, INPUT);
    pinMode(MOSFET_PIN, OUTPUT);
    digitalWrite(MOSFET_PIN, LOW);

    Serial.println("[sensors] Aero Monitor init complete");
    return ds18b20Ok;
}

static float adcAvg(int pin, int samples = 32) {
    uint32_t sum = 0;
    for (int i = 0; i < samples; i++) { sum += analogRead(pin); delayMicroseconds(200); }
    return float(sum) / float(samples) / 4095.0f * 3.3f;
}

static float readDistance() {
    digitalWrite(ULTRA_TRIG_PIN, LOW); delayMicroseconds(2);
    digitalWrite(ULTRA_TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(ULTRA_TRIG_PIN, LOW);
    long d = pulseIn(ULTRA_ECHO_PIN, HIGH, 30000);
    if (d == 0) return -1.0f;
    float cm = d * 0.0173f;
    return (cm >= 2.0f && cm <= 500.0f) ? cm : -1.0f;
}

AeroReading sensors_read_all() {
    AeroReading r = {};

    digitalWrite(MOSFET_PIN, HIGH);
    delay(PROBE_WARMUP_MS);

    // Water temp
    if (ds18b20Ok) {
        ds18b20.requestTemperatures();
        float c = ds18b20.getTempCByIndex(0);
        r.temp_valid = (c != DEVICE_DISCONNECTED_C);
        if (r.temp_valid) r.water_temp_f = roundf((c * 1.8f + 32.0f) * 10.0f) / 10.0f;
    }

    // pH
    float phV = adcAvg(PH_ADC_PIN);
    float slope = 3.0f / (PH_VOLTAGE_AT_7 - PH_VOLTAGE_AT_4);
    r.ph = constrain(7.0f + slope * (phV - PH_VOLTAGE_AT_7), 0.0f, 14.0f);
    r.ph = roundf(r.ph * 100.0f) / 100.0f;

    // EC
    float ecV = adcAvg(EC_ADC_PIN);
    float waterC = r.temp_valid ? (r.water_temp_f - 32.0f) / 1.8f : 25.0f;
    float comp = 1.0f + EC_TEMP_COEFF * (waterC - 25.0f);
    r.ec_ms = roundf(max(ecV * EC_K_VALUE / comp, 0.0f) * 100.0f) / 100.0f;
    r.ppm = (uint16_t)(r.ec_ms * 500.0f);

    // Water level
    float dist = readDistance();
    r.level_valid = (dist > 0);
    if (r.level_valid) {
        float range = float(TANK_DEPTH_CM - TANK_FULL_CM);
        r.water_level_pct = constrain(100.0f * (TANK_DEPTH_CM - dist) / range, 0.0f, 100.0f);
    }

    // Mist pressure
    float pressV = adcAvg(PRESSURE_ADC_PIN);
    // Undo voltage divider: actual V = pressV * (R1+R2)/R2
    float actualV = pressV * float(PRESSURE_R1 + PRESSURE_R2) / float(PRESSURE_R2);
    if (actualV >= PRESSURE_V_MIN) {
        r.mist_pressure_psi = (actualV - PRESSURE_V_MIN) / (PRESSURE_V_MAX - PRESSURE_V_MIN) * PRESSURE_MAX_PSI;
        r.mist_pressure_psi = roundf(constrain(r.mist_pressure_psi, 0.0f, PRESSURE_MAX_PSI) * 10.0f) / 10.0f;
        r.pressure_valid = true;
    }

    digitalWrite(MOSFET_PIN, LOW);
    return r;
}

void aero_to_json(const AeroReading& r, char* buf, size_t len) {
    JsonDocument doc;
    if (r.temp_valid) doc["water_temp_f"]     = r.water_temp_f;
    doc["ph"]  = r.ph;
    doc["ec"]  = r.ec_ms;
    doc["ppm"] = r.ppm;
    if (r.level_valid) doc["water_level_pct"]  = r.water_level_pct;
    if (r.pressure_valid) doc["mist_pressure"] = r.mist_pressure_psi;
    serializeJson(doc, buf, len);
}

} // namespace tendril
