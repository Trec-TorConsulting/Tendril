#include "sensors.h"
#include "config.h"
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

static Adafruit_BME680 bme;
static bool bmeOk = false;

static OneWire oneWire(ONEWIRE_PIN);
static DallasTemperature ds18b20(&oneWire);
static bool ds18b20Ok = false;

namespace tendril {

bool sensors_begin() {
    Wire.begin(I2C_SDA, I2C_SCL);

    if (bme.begin(0x77, &Wire) || bme.begin(0x76, &Wire)) {
        bmeOk = true;
        bme.setTemperatureOversampling(BME680_OS_8X);
        bme.setHumidityOversampling(BME680_OS_2X);
        bme.setPressureOversampling(BME680_OS_4X);
        bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
        bme.setGasHeater(320, 150);
        Serial.println("[sensors] BME680 OK");
    } else {
        Serial.println("[sensors] BME680 not found");
    }

    ds18b20.begin();
    if (ds18b20.getDeviceCount() > 0) {
        ds18b20Ok = true;
        ds18b20.setResolution(12);  // 12-bit = 0.0625°C
        Serial.printf("[sensors] DS18B20 OK (%d device(s))\n", ds18b20.getDeviceCount());
    } else {
        Serial.println("[sensors] DS18B20 not found");
    }

    pinMode(SOIL_SENSOR_PIN, INPUT);
    pinMode(PH_ADC_PIN, INPUT);
    pinMode(EC_ADC_PIN, INPUT);

    if (PROBE_POWER_PIN >= 0) {
        pinMode(PROBE_POWER_PIN, OUTPUT);
        digitalWrite(PROBE_POWER_PIN, LOW);
    }

    Serial.println("[sensors] Soil Pro init complete");
    return bmeOk;
}

SoilReading sensors_read_soil() {
    // Soil moisture
    uint32_t sum = 0;
    for (int i = 0; i < 16; i++) {
        sum += analogRead(SOIL_SENSOR_PIN);
        delayMicroseconds(200);
    }
    int raw = sum / 16;
    int pct = map(constrain(raw, SOIL_WET_VALUE, SOIL_DRY_VALUE),
                  SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100);
    pct = constrain(pct, 0, 100);

    // Soil temperature
    float tempF = -127.0f;
    bool tempValid = false;
    if (ds18b20Ok) {
        ds18b20.requestTemperatures();
        float tempC = ds18b20.getTempCByIndex(0);
        if (tempC != DEVICE_DISCONNECTED_C) {
            tempF = tempC * 9.0f / 5.0f + 32.0f;
            tempValid = true;
        }
    }

    return SoilReading{
        .moisture_pct = pct,
        .soil_temp_f  = tempValid ? roundf(tempF * 10.0f) / 10.0f : 0.0f,
        .temp_valid   = tempValid,
        .valid        = true,
    };
}

RunoffReading sensors_read_runoff(float solution_temp_c) {
    // Power on probes
    if (PROBE_POWER_PIN >= 0) {
        digitalWrite(PROBE_POWER_PIN, HIGH);
        delay(PROBE_WARMUP_MS);
    }

    // Read pH
    uint32_t phSum = 0;
    for (int i = 0; i < 32; i++) {
        phSum += analogRead(PH_ADC_PIN);
        delayMicroseconds(200);
    }
    float phVoltage = (float(phSum) / 32.0f / 4095.0f) * 3.3f;
    float slope = (7.0f - 4.0f) / (PH_VOLTAGE_AT_7 - PH_VOLTAGE_AT_4);
    float ph = 7.0f + slope * (phVoltage - PH_VOLTAGE_AT_7);
    ph = constrain(ph, 0.0f, 14.0f);

    // Read EC
    uint32_t ecSum = 0;
    for (int i = 0; i < 32; i++) {
        ecSum += analogRead(EC_ADC_PIN);
        delayMicroseconds(200);
    }
    float ecVoltage = (float(ecSum) / 32.0f / 4095.0f) * 3.3f;
    float ecRaw = ecVoltage * EC_K_VALUE;
    // Temperature compensation
    float tempComp = 1.0f + EC_TEMP_COEFF * (solution_temp_c - 25.0f);
    float ec = ecRaw / tempComp;
    ec = max(ec, 0.0f);

    // Power off probes
    if (PROBE_POWER_PIN >= 0) {
        digitalWrite(PROBE_POWER_PIN, LOW);
    }

    return RunoffReading{
        .ph     = roundf(ph * 100.0f) / 100.0f,
        .ec_ms  = roundf(ec * 100.0f) / 100.0f,
        .ppm    = (uint16_t)(ec * 500.0f),
        .valid  = true,
    };
}

AmbientReading sensors_read_ambient() {
    if (!bmeOk || !bme.performReading()) {
        return AmbientReading{.valid = false};
    }
    float tempF = bme.temperature * 9.0f / 5.0f + 32.0f;
    return AmbientReading{
        .temp_f       = roundf(tempF * 10.0f) / 10.0f,
        .humidity     = roundf(bme.humidity * 10.0f) / 10.0f,
        .pressure_hpa = roundf(bme.pressure / 100.0f * 10.0f) / 10.0f,
        .gas_kohms    = roundf(bme.gas_resistance / 1000.0f * 10.0f) / 10.0f,
        .valid        = true,
    };
}

void soil_to_json(const SoilReading& r, char* buf, size_t len) {
    JsonDocument doc;
    doc["soil_moisture"] = r.moisture_pct;
    doc["position"] = 1;
    if (r.temp_valid) doc["soil_temp"] = r.soil_temp_f;
    serializeJson(doc, buf, len);
}

void runoff_to_json(const RunoffReading& r, char* buf, size_t len) {
    JsonDocument doc;
    doc["runoff_ph"] = r.ph;
    doc["runoff_ec"] = r.ec_ms;
    doc["ppm"]       = r.ppm;
    serializeJson(doc, buf, len);
}

void ambient_to_json(const AmbientReading& r, char* buf, size_t len) {
    JsonDocument doc;
    doc["ambient_temp_f"]   = r.temp_f;
    doc["ambient_humidity"] = r.humidity;
    doc["pressure_hpa"]     = r.pressure_hpa;
    doc["gas_kohms"]        = r.gas_kohms;
    serializeJson(doc, buf, len);
}

} // namespace tendril
