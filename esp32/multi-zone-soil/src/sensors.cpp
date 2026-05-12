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

static const int soilPins[4] = { SOIL_PIN_1, SOIL_PIN_2, SOIL_PIN_3, SOIL_PIN_4 };

// Store DS18B20 ROM addresses for stable zone mapping
static DeviceAddress tempAddrs[4];
static int tempCount = 0;

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
    }

    ds18b20.begin();
    tempCount = min((int)ds18b20.getDeviceCount(), NUM_ZONES);
    for (int i = 0; i < tempCount; i++) {
        ds18b20.getAddress(tempAddrs[i], i);
        ds18b20.setResolution(tempAddrs[i], 12);
        Serial.printf("[sensors] DS18B20 zone %d: ", i + 1);
        for (int b = 0; b < 8; b++) Serial.printf("%02X", tempAddrs[i][b]);
        Serial.println();
    }
    Serial.printf("[sensors] %d DS18B20 probes found\n", tempCount);

    for (int i = 0; i < NUM_ZONES; i++) {
        pinMode(soilPins[i], INPUT);
    }

    return bmeOk;
}

static int readSoilPct(int pin) {
    uint32_t sum = 0;
    for (int i = 0; i < 16; i++) { sum += analogRead(pin); delayMicroseconds(200); }
    int raw = sum / 16;
    return constrain(map(constrain(raw, SOIL_WET_VALUE, SOIL_DRY_VALUE),
                         SOIL_DRY_VALUE, SOIL_WET_VALUE, 0, 100), 0, 100);
}

void sensors_read_zones(ZoneReading zones[], int count) {
    ds18b20.requestTemperatures();

    for (int i = 0; i < count && i < NUM_ZONES; i++) {
        zones[i].zone = i + 1;
        zones[i].moisture_pct = readSoilPct(soilPins[i]);

        if (i < tempCount) {
            float c = ds18b20.getTempC(tempAddrs[i]);
            zones[i].temp_valid = (c != DEVICE_DISCONNECTED_C);
            if (zones[i].temp_valid) {
                zones[i].soil_temp_f = roundf((c * 1.8f + 32.0f) * 10.0f) / 10.0f;
            }
        } else {
            zones[i].temp_valid = false;
        }
    }
}

AmbientReading sensors_read_ambient() {
    if (!bmeOk || !bme.performReading()) return AmbientReading{.valid = false};
    return AmbientReading{
        .temp_f       = roundf((bme.temperature * 1.8f + 32.0f) * 10.0f) / 10.0f,
        .humidity     = roundf(bme.humidity * 10.0f) / 10.0f,
        .pressure_hpa = roundf(bme.pressure / 100.0f * 10.0f) / 10.0f,
        .gas_kohms    = roundf(bme.gas_resistance / 1000.0f * 10.0f) / 10.0f,
        .valid        = true,
    };
}

void zones_to_json(const ZoneReading zones[], int count, char* buf, size_t len) {
    JsonDocument doc;
    JsonArray arr = doc["zones"].to<JsonArray>();
    for (int i = 0; i < count; i++) {
        JsonObject z = arr.add<JsonObject>();
        z["zone"]          = zones[i].zone;
        z["soil_moisture"]  = zones[i].moisture_pct;
        if (zones[i].temp_valid) {
            z["soil_temp"] = zones[i].soil_temp_f;
        }
    }
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
