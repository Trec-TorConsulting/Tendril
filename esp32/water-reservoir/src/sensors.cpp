#include "sensors.h"
#include "config.h"
#include <Arduino.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

static OneWire oneWire(ONEWIRE_PIN);
static DallasTemperature ds18b20(&oneWire);
static bool dsOk = false;

// ─── Flow pulse counter (interrupt-driven) ──────────
static volatile uint32_t flowPulses = 0;
static float totalLitres = 0.0f;

static void IRAM_ATTR flowISR() { flowPulses++; }

// ─── Ultrasonic helper ──────────────────────────────
static float readDistanceCm() {
    // JSN-SR04T trigger/echo
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    // Average 3 readings
    float sum = 0;
    int good = 0;
    for (int i = 0; i < 3; i++) {
        digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
        digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(20);
        digitalWrite(TRIG_PIN, LOW);

        long duration = pulseIn(ECHO_PIN, HIGH, 30000); // timeout ~5 m
        if (duration > 0) {
            sum += duration * 0.0343f / 2.0f;
            good++;
        }
        delay(60); // JSN-SR04T needs ~60 ms between pings
    }
    return (good > 0) ? sum / good : -1.0f;
}

namespace tendril {

bool sensors_begin() {
    // Enable 5V rail
    pinMode(MOSFET_GATE_PIN, OUTPUT);
    digitalWrite(MOSFET_GATE_PIN, HIGH);
    delay(POWER_STABILIZE_MS);

    // DS18B20
    ds18b20.begin();
    if (ds18b20.getDeviceCount() > 0) {
        ds18b20.setResolution(12);
        dsOk = true;
        Serial.println("[sensors] DS18B20 OK");
    } else {
        Serial.println("[sensors] DS18B20 not found");
    }

    // Flow sensor interrupt
    pinMode(FLOW_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(FLOW_PIN), flowISR, RISING);
    Serial.println("[sensors] YF-S201 interrupt attached");

    Serial.println("[sensors] JSN-SR04T ready");
    return true;
}

ReservoirReading sensors_read_all() {
    ReservoirReading r = {};

    // ── Water level (ultrasonic) ──
    float dist = readDistanceCm();
    if (dist > 0 && dist < 450) {
        r.water_level_cm = TANK_DEPTH_CM - dist + SENSOR_OFFSET_CM;
        if (r.water_level_cm < 0) r.water_level_cm = 0;
        r.water_level_pct = constrain(
            (int)(r.water_level_cm / (float)TANK_FULL_CM * 100.0f), 0, 100);
        r.level_valid = true;
    }

    // ── Water temperature ──
    if (dsOk) {
        ds18b20.requestTemperatures();
        float c = ds18b20.getTempCByIndex(0);
        if (c != DEVICE_DISCONNECTED_C) {
            r.water_temp_f = roundf((c * 1.8f + 32.0f) * 10.0f) / 10.0f;
            r.temp_valid = true;
        }
    }

    // ── Flow rate ──
    noInterrupts();
    uint32_t pulses = flowPulses;
    flowPulses = 0;
    interrupts();

    // Calculate flow from accumulated pulses since last wake (≈ brief window)
    // For proper flow measurement, we count during FLOW_WINDOW_MS
    delay(FLOW_WINDOW_MS);
    noInterrupts();
    uint32_t windowPulses = flowPulses;
    flowPulses = 0;
    interrupts();

    if (windowPulses > 0) {
        float freq = (float)windowPulses / ((float)FLOW_WINDOW_MS / 1000.0f);
        r.flow_lpm = freq / FLOW_FACTOR;
        r.flow_valid = true;
    }

    // Accumulate total volume (rough — only measured while awake)
    float litresThisCycle = (pulses + windowPulses) / (FLOW_FACTOR * 60.0f);
    totalLitres += litresThisCycle;
    r.total_litres = totalLitres;

    return r;
}

void reservoir_to_json(const ReservoirReading& r, char* buf, size_t len) {
    JsonDocument doc;
    if (r.level_valid) {
        doc["water_level_cm"]  = roundf(r.water_level_cm * 10.0f) / 10.0f;
        doc["water_level_pct"] = r.water_level_pct;
    }
    if (r.temp_valid) {
        doc["water_temp_f"] = r.water_temp_f;
    }
    if (r.flow_valid) {
        doc["flow_lpm"] = roundf(r.flow_lpm * 100.0f) / 100.0f;
    }
    doc["total_litres"] = roundf(r.total_litres * 10.0f) / 10.0f;
    serializeJson(doc, buf, len);
}

} // namespace tendril
