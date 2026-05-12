#include "sensors.h"
#include "config.h"

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <ArduinoJson.h>

static Adafruit_BME680 bme;
static bool bmeOk = false;

namespace tendril {

bool sensors_begin() {
    Wire.begin(I2C_SDA, I2C_SCL);

    // Try both common BME680 I2C addresses
    if (bme.begin(0x77, &Wire)) {
        bmeOk = true;
    } else if (bme.begin(0x76, &Wire)) {
        bmeOk = true;
    }

    if (bmeOk) {
        bme.setTemperatureOversampling(BME680_OS_8X);
        bme.setHumidityOversampling(BME680_OS_2X);
        bme.setPressureOversampling(BME680_OS_4X);
        bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
        bme.setGasHeater(320, 150);
        Serial.println("[sensors] BME680 OK");
    } else {
        Serial.println("[sensors] BME680 not found — ambient disabled");
    }

    pinMode(SOIL_SENSOR_PIN, INPUT);
    Serial.println("[sensors] Soil moisture ADC OK");

    return bmeOk;
}

SoilReading sensors_read_soil() {
    // Multi-sample averaging for ADC stability
    uint32_t sum = 0;
    for (int i = 0; i < 16; i++) {
        sum += analogRead(SOIL_SENSOR_PIN);
        delayMicroseconds(200);
    }
    int raw = static_cast<int>(sum / 16);

    int wetVal = SOIL_WET_VALUE;
    int dryVal = SOIL_DRY_VALUE;
    int clamped = constrain(raw, wetVal, dryVal);
    int pct = map(clamped, dryVal, wetVal, 0, 100);
    pct = constrain(pct, 0, 100);

    return SoilReading{
        .moisture_pct = pct,
        .raw_adc      = raw,
        .valid        = true,
    };
}

AmbientReading sensors_read_ambient() {
    if (!bmeOk) {
        return AmbientReading{.valid = false};
    }

    if (!bme.performReading()) {
        Serial.println("[sensors] BME680 read failed");
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
    doc["position"]      = 1;
    doc["raw_adc"]       = r.raw_adc;
    serializeJson(doc, buf, len);
}

void ambient_to_json(const AmbientReading& r, char* buf, size_t len) {
    JsonDocument doc;
    doc["ambient_temp_f"]    = r.temp_f;
    doc["ambient_humidity"]  = r.humidity;
    doc["pressure_hpa"]      = r.pressure_hpa;
    doc["gas_kohms"]         = r.gas_kohms;
    serializeJson(doc, buf, len);
}

} // namespace tendril
