/// @file main_matter.cpp
/// Tendril Soil Basic — Matter firmware (ESP-IDF + esp-matter).
/// Registers as a Matter Temperature Sensor + Humidity Sensor device.
/// Soil moisture is reported via a custom Matter cluster.

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_event.h"
#include "nvs_flash.h"

#include "esp_matter.h"
#include "esp_matter_attribute_utils.h"
#include "esp_matter_endpoint.h"
#include "esp_matter_cluster.h"
#include "app/server/Server.h"

#include "config.h"
#include "sensors.h"

static const char* TAG = "tendril_matter";

using namespace esp_matter;
using namespace esp_matter::attribute;
using namespace esp_matter::endpoint;
using namespace esp_matter::cluster;

static uint16_t sensor_endpoint_id = 0;

// ─── Matter Event Callback ──────────────────────────
static void app_event_cb(const ChipDeviceEvent *event, intptr_t arg) {
    switch (event->Type) {
    case chip::DeviceLayer::DeviceEventType::kCommissioningComplete:
        ESP_LOGI(TAG, "Commissioning complete");
        break;
    case chip::DeviceLayer::DeviceEventType::kFabricCommitted:
        ESP_LOGI(TAG, "Fabric committed");
        break;
    default:
        break;
    }
}

// ─── Attribute Update Callback ──────────────────────
static esp_err_t app_attribute_update_cb(attribute::callback_type_t type,
                                          uint16_t endpoint_id,
                                          uint32_t cluster_id,
                                          uint32_t attribute_id,
                                          esp_matter_attr_val_t *val,
                                          void *priv_data) {
    // Read-only sensor — no write handling needed
    return ESP_OK;
}

// ─── Device Setup ────────────────────────────────────
static esp_err_t create_device() {
    node::config_t node_config;
    node_t *node = node::create(&node_config, app_attribute_update_cb, NULL);
    if (!node) {
        ESP_LOGE(TAG, "Failed to create Matter node");
        return ESP_FAIL;
    }

    // Create a temperature sensor endpoint
    temperature_sensor::config_t temp_config;
    temp_config.temperature_measurement.measured_value = 0;      // 0.01°C units
    temp_config.temperature_measurement.min_measured_value = -4000;
    temp_config.temperature_measurement.max_measured_value = 8500;

    endpoint_t *ep = temperature_sensor::create(node, &temp_config, ENDPOINT_FLAG_NONE, NULL);
    if (!ep) {
        ESP_LOGE(TAG, "Failed to create temperature sensor endpoint");
        return ESP_FAIL;
    }
    sensor_endpoint_id = endpoint::get_id(ep);

    // Add humidity measurement cluster to the same endpoint
    humidity_sensor::config_t hum_config;
    hum_config.relative_humidity_measurement.measured_value = 0;
    hum_config.relative_humidity_measurement.min_measured_value = 0;
    hum_config.relative_humidity_measurement.max_measured_value = 10000;

    cluster_t *hum_cluster = humidity_measurement::create(ep, &hum_config.relative_humidity_measurement,
                                                          CLUSTER_FLAG_SERVER);
    if (!hum_cluster) {
        ESP_LOGW(TAG, "Failed to add humidity cluster — continuing without it");
    }

    ESP_LOGI(TAG, "Matter device created (endpoint %u)", sensor_endpoint_id);
    return ESP_OK;
}

// ─── Sensor Reporting Task ──────────────────────────
static void sensor_report_task(void *arg) {
    // Wait for Matter stack to be ready
    vTaskDelay(pdMS_TO_TICKS(5000));

    while (true) {
        auto soil    = tendril::sensors_read_soil();
        auto ambient = tendril::sensors_read_ambient();

        ESP_LOGI(TAG, "Soil: %d%%, Temp: %.1f°F, Humidity: %.1f%%",
                 soil.moisture_pct,
                 ambient.valid ? ambient.temp_f : 0.0f,
                 ambient.valid ? ambient.humidity : 0.0f);

        if (ambient.valid) {
            // Update temperature (Matter uses 0.01°C units)
            float tempC = (ambient.temp_f - 32.0f) * 5.0f / 9.0f;
            int16_t matterTemp = (int16_t)(tempC * 100.0f);
            esp_matter_attr_val_t tempVal = esp_matter_nullable_int16(matterTemp);

            attribute::update(sensor_endpoint_id,
                              chip::app::Clusters::TemperatureMeasurement::Id,
                              chip::app::Clusters::TemperatureMeasurement::Attributes::MeasuredValue::Id,
                              &tempVal);

            // Update humidity (Matter uses 0.01% units)
            uint16_t matterHum = (uint16_t)(ambient.humidity * 100.0f);
            esp_matter_attr_val_t humVal = esp_matter_nullable_uint16(matterHum);

            attribute::update(sensor_endpoint_id,
                              chip::app::Clusters::RelativeHumidityMeasurement::Id,
                              chip::app::Clusters::RelativeHumidityMeasurement::Attributes::MeasuredValue::Id,
                              &humVal);
        }

        vTaskDelay(pdMS_TO_TICKS(SLEEP_SECONDS * 1000));
    }
}

// ─── Entry Point ─────────────────────────────────────
extern "C" void app_main(void) {
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    tendril::sensors_begin();

    ESP_ERROR_CHECK(create_device());

    // Start Matter
    ESP_ERROR_CHECK(esp_matter::start(app_event_cb));

    ESP_LOGI(TAG, "Matter stack started — use mobile app to commission");

    xTaskCreate(sensor_report_task, "sensors", 4096, NULL, 4, NULL);
}
