#include "sensors.h"
#include "config.h"
#include <Wire.h>
#include <math.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <SensirionI2CScd4x.h>
#include <BH1750.h>
#include <ArduinoJson.h>

static Adafruit_BME680 bme;
static bool bmeOk = false;
static SensirionI2CScd4x scd41;
static bool scdOk = false;
static BH1750 lightMeter;
static bool luxOk = false;

namespace tendril {

bool sensors_begin() {
    Wire.begin(I2C_SDA, I2C_SCL);

    // BME680
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

    // SCD41 CO₂
    scd41.begin(Wire);
    uint16_t err = scd41.stopPeriodicMeasurement();
    if (err == 0) {
        scd41.setSensorAltitude(ALTITUDE_M);
        scdOk = true;
        Serial.println("[sensors] SCD41 OK");
    } else {
        Serial.println("[sensors] SCD41 not found");
    }

    // BH1750 light sensor
    if (lightMeter.begin(BH1750::ONE_TIME_HIGH_RES_MODE)) {
        luxOk = true;
        Serial.println("[sensors] BH1750 OK");
    } else {
        Serial.println("[sensors] BH1750 not found");
    }

    return bmeOk || scdOk;
}

static float calcVPD(float tempC, float rh) {
    // Tetens formula
    float svp = 0.6108f * expf(17.27f * tempC / (tempC + 237.3f));
    return svp * (1.0f - rh / 100.0f);
}

static float calcDewPoint(float tempC, float rh) {
    float a = 17.27f, b = 237.3f;
    float gamma = (a * tempC / (b + tempC)) + logf(rh / 100.0f);
    return b * gamma / (a - gamma);
}

EnvironmentReading sensors_read_all() {
    EnvironmentReading r = {};

    // Start SCD41 single-shot measurement (takes ~5 s)
    if (scdOk) {
        scd41.measureSingleShot();
    }

    // Read BME680 while SCD41 measures
    if (bmeOk && bme.performReading()) {
        r.bme_valid = true;
        float tempC = bme.temperature;
        r.temp_f       = roundf((tempC * 1.8f + 32.0f) * 10.0f) / 10.0f;
        r.humidity     = roundf(bme.humidity * 10.0f) / 10.0f;
        r.pressure_hpa = roundf(bme.pressure / 100.0f * 10.0f) / 10.0f;
        r.gas_kohms    = roundf(bme.gas_resistance / 1000.0f * 10.0f) / 10.0f;
        r.vpd_kpa      = roundf(calcVPD(tempC, bme.humidity) * 100.0f) / 100.0f;
        float dpC = calcDewPoint(tempC, bme.humidity);
        r.dew_point_f  = roundf((dpC * 1.8f + 32.0f) * 10.0f) / 10.0f;
    }

    // Read BH1750
    if (luxOk) {
        float lux = lightMeter.readLightLevel();
        if (lux >= 0) {
            r.lux = roundf(lux);
            r.lux_valid = true;
        }
    }

    // Wait for SCD41 result
    if (scdOk) {
        delay(CO2_MEASUREMENT_MS);
        uint16_t co2 = 0;
        float scdTemp = 0, scdHum = 0;
        uint16_t err = scd41.readMeasurement(co2, scdTemp, scdHum);
        if (err == 0 && co2 > 0) {
            r.co2_ppm = co2;
            r.co2_valid = true;
        }
    }

    return r;
}

void env_to_json(const EnvironmentReading& r, char* buf, size_t len) {
    JsonDocument doc;
    if (r.bme_valid) {
        doc["ambient_temp_f"]   = r.temp_f;
        doc["ambient_humidity"] = r.humidity;
        doc["vpd"]              = r.vpd_kpa;
        doc["dew_point_f"]      = r.dew_point_f;
        doc["air_pressure"]     = r.pressure_hpa;
        doc["voc"]              = r.gas_kohms;
    }
    if (r.co2_valid) doc["co2"]  = r.co2_ppm;
    if (r.lux_valid) doc["lux"]  = r.lux;
    serializeJson(doc, buf, len);
}

} // namespace tendril
