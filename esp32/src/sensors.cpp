#include "sensors.h"
#include "config.h"
#include "mqtt_client.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>

// ─── Hardware instances ──────────────────────────────
static Adafruit_BME680 bme;
static bool bmeOk = false;

// ─── Soil moisture helpers ───────────────────────────
// Capacitive sensor output: HIGH when dry, LOW when wet
// Map raw ADC (12-bit, 0-4095) to 0-100% moisture
static int readSoilPercent(int pin, int dryVal, int wetVal) {
    // Average 8 samples to reduce noise
    long sum = 0;
    for (int i = 0; i < 8; i++) {
        sum += analogRead(pin);
        delay(2);
    }
    int raw = sum / 8;

    // Constrain and map — dry=high, wet=low → invert
    int pct = map(constrain(raw, wetVal, dryVal), dryVal, wetVal, 0, 100);
    return constrain(pct, 0, 100);
}

// ─── Celsius to Fahrenheit ───────────────────────────
static float cToF(float c) {
    return c * 9.0f / 5.0f + 32.0f;
}

// ─── Setup ───────────────────────────────────────────
bool sensors_setup() {
    // I2C bus
    Wire.begin(I2C_SDA, I2C_SCL);

    // BME680 — try default address 0x77, fallback to 0x76
    if (bme.begin(0x77, &Wire)) {
        bmeOk = true;
    } else if (bme.begin(0x76, &Wire)) {
        bmeOk = true;
    }

    if (bmeOk) {
        // Configure oversampling and filter for indoor use
        bme.setTemperatureOversampling(BME680_OS_8X);
        bme.setHumidityOversampling(BME680_OS_2X);
        bme.setPressureOversampling(BME680_OS_4X);
        bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
        // Gas sensor heater: 320°C for 150ms
        bme.setGasHeater(320, 150);
        Serial.println("BME680 initialized");
    } else {
        Serial.println("WARNING: BME680 not found! Ambient readings disabled.");
    }

    // Soil sensor pin — input only (no pullup needed for capacitive)
    pinMode(SOIL_SENSOR_1_PIN, INPUT);
    Serial.println("Soil sensor initialized");

    return bmeOk;
}

// ─── Read and publish ────────────────────────────────
void sensors_read_and_publish() {
    // ── Soil / bucket-level readings ─────────────────
    int soil1 = readSoilPercent(SOIL_SENSOR_1_PIN, SOIL_1_DRY_VALUE, SOIL_1_WET_VALUE);

    {
        JsonDocument doc;
        doc["soil_moisture"] = soil1;
        doc["position"] = 1;
        char payload[128];
        serializeJson(doc, payload, sizeof(payload));
        mqtt_publish("readings", payload);
        Serial.printf("Soil: %d%%\n", soil1);
    }

    // ── Ambient / tent-level readings (BME680) ───────
    if (bmeOk && bme.performReading()) {
        float tempF = cToF(bme.temperature);
        float humidity = bme.humidity;
        float pressureHpa = bme.pressure / 100.0f;
        float gasKohms = bme.gas_resistance / 1000.0f;

        JsonDocument ambient;
        ambient["ambient_temp_f"] = round(tempF * 10.0f) / 10.0f;
        ambient["ambient_humidity"] = round(humidity * 10.0f) / 10.0f;
        ambient["pressure_hpa"] = round(pressureHpa * 10.0f) / 10.0f;
        ambient["gas_kohms"] = round(gasKohms * 10.0f) / 10.0f;

        char payload[256];
        serializeJson(ambient, payload, sizeof(payload));
        mqtt_publish("ambient", payload);

        Serial.printf("BME680: %.1f°F, %.1f%% RH, %.1f hPa, %.1f kΩ gas\n",
                       tempF, humidity, pressureHpa, gasKohms);
    } else if (bmeOk) {
        Serial.println("BME680 read failed");
    }
}
