/// @file main_zigbee.cpp
/// Tendril Soil Basic — Zigbee 3.0 firmware (ESP-IDF + esp-zigbee-sdk).
/// Operates as a Zigbee Sleepy End Device.  Reports soil moisture via
/// the Soil Moisture Measurement cluster (0x0408) and ambient via
/// Temperature (0x0402) + Relative Humidity (0x0405) clusters.

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_sleep.h"
#include "nvs_flash.h"
#include "ha/esp_zigbee_ha_standard.h"
#include "esp_zigbee_core.h"

#include "config.h"
#include "sensors.h"

static const char* TAG = "tendril_zb";

// ─── Zigbee Configuration ────────────────────────────
#define TENDRIL_ENDPOINT        1
#define TENDRIL_PROFILE_ID      ESP_ZB_AF_HA_PROFILE_ID
#define TENDRIL_DEVICE_ID       ESP_ZB_HA_SIMPLE_SENSOR_DEVICE_ID

// Cluster IDs
#define ZB_TEMP_CLUSTER         ESP_ZB_ZCL_CLUSTER_ID_TEMP_MEASUREMENT
#define ZB_HUMIDITY_CLUSTER     ESP_ZB_ZCL_CLUSTER_ID_REL_HUMIDITY_MEASUREMENT
#define ZB_SOIL_CLUSTER         0x0408  // Soil Moisture Measurement (ZCL 7.0)
#define ZB_POWER_CLUSTER        ESP_ZB_ZCL_CLUSTER_ID_POWER_CONFIG

// ─── Zigbee Callbacks ────────────────────────────────
static void bdb_start_top_level_commissioning_cb(uint8_t mode_mask) {
    ESP_ERROR_CHECK(esp_zb_bdb_start_top_level_commissioning(mode_mask));
}

static void esp_zb_app_signal_handler(esp_zb_app_signal_t *signal) {
    uint32_t *p_sg_p = signal->p_app_signal;
    esp_err_t err = signal->esp_err_status;
    esp_zb_app_signal_type_t sig_type = (esp_zb_app_signal_type_t)*p_sg_p;

    switch (sig_type) {
    case ESP_ZB_ZDO_SIGNAL_SKIP_STARTUP:
        ESP_LOGI(TAG, "Zigbee stack initialized");
        esp_zb_bdb_start_top_level_commissioning(ESP_ZB_BDB_MODE_INITIALIZATION);
        break;

    case ESP_ZB_BDB_SIGNAL_DEVICE_FIRST_START:
    case ESP_ZB_BDB_SIGNAL_DEVICE_REBOOT:
        if (err == ESP_OK) {
            ESP_LOGI(TAG, "Device started — joining network");
            esp_zb_bdb_start_top_level_commissioning(ESP_ZB_BDB_MODE_NETWORK_STEERING);
        } else {
            ESP_LOGW(TAG, "Failed to initialize (0x%x), retrying...", err);
            esp_zb_scheduler_alarm(bdb_start_top_level_commissioning_cb,
                                   ESP_ZB_BDB_MODE_NETWORK_STEERING, 1000);
        }
        break;

    case ESP_ZB_BDB_SIGNAL_STEERING:
        if (err == ESP_OK) {
            esp_zb_ieee_addr_t extended_pan;
            esp_zb_get_extended_pan_id(extended_pan);
            ESP_LOGI(TAG, "Joined network (PAN: %02x:%02x:%02x:%02x:%02x:%02x:%02x:%02x, ch:%d)",
                     extended_pan[7], extended_pan[6], extended_pan[5], extended_pan[4],
                     extended_pan[3], extended_pan[2], extended_pan[1], extended_pan[0],
                     esp_zb_get_current_channel());
        }
        break;

    default:
        ESP_LOGI(TAG, "Signal %d, status: %d", sig_type, err);
        break;
    }
}

// ─── Cluster Setup ───────────────────────────────────
static esp_zb_cluster_list_t* create_cluster_list() {
    esp_zb_cluster_list_t *cluster_list = esp_zb_zcl_cluster_list_create();

    // Basic cluster (required)
    esp_zb_basic_cluster_cfg_t basic_cfg = {
        .zcl_version = ESP_ZB_ZCL_BASIC_ZCL_VERSION_DEFAULT_VALUE,
        .power_source = 0x03,  // Battery
    };
    esp_zb_attribute_list_t *basic_cluster = esp_zb_basic_cluster_create(&basic_cfg);
    esp_zb_basic_cluster_add_attr(basic_cluster, ESP_ZB_ZCL_ATTR_BASIC_MANUFACTURER_NAME_ID,
                                  (void*)"Tendril");
    esp_zb_basic_cluster_add_attr(basic_cluster, ESP_ZB_ZCL_ATTR_BASIC_MODEL_IDENTIFIER_ID,
                                  (void*)"Soil Basic");
    ESP_ERROR_CHECK(esp_zb_cluster_list_add_basic_cluster(cluster_list, basic_cluster,
                                                          ESP_ZB_ZCL_CLUSTER_SERVER_ROLE));

    // Power configuration (battery reporting)
    esp_zb_power_config_cluster_cfg_t power_cfg = {};
    esp_zb_attribute_list_t *power_cluster = esp_zb_power_config_cluster_create(&power_cfg);
    ESP_ERROR_CHECK(esp_zb_cluster_list_add_power_config_cluster(cluster_list, power_cluster,
                                                                  ESP_ZB_ZCL_CLUSTER_SERVER_ROLE));

    // Temperature measurement
    esp_zb_temperature_meas_cluster_cfg_t temp_cfg = {
        .measured_value = 0,
        .min_value = -4000,  // -40.00 °C
        .max_value = 8500,   //  85.00 °C
    };
    esp_zb_attribute_list_t *temp_cluster = esp_zb_temperature_meas_cluster_create(&temp_cfg);
    ESP_ERROR_CHECK(esp_zb_cluster_list_add_temperature_meas_cluster(cluster_list, temp_cluster,
                                                                      ESP_ZB_ZCL_CLUSTER_SERVER_ROLE));

    // Relative humidity measurement
    esp_zb_humidity_meas_cluster_cfg_t hum_cfg = {
        .measured_value = 0,
        .min_value = 0,
        .max_value = 10000,  // 100.00 %
    };
    esp_zb_attribute_list_t *hum_cluster = esp_zb_humidity_meas_cluster_create(&hum_cfg);
    ESP_ERROR_CHECK(esp_zb_cluster_list_add_humidity_meas_cluster(cluster_list, hum_cluster,
                                                                    ESP_ZB_ZCL_CLUSTER_SERVER_ROLE));

    return cluster_list;
}

// ─── Reporting Task ──────────────────────────────────
static void sensor_report_task(void *arg) {
    while (true) {
        // Read sensors
        auto soil    = tendril::sensors_read_soil();
        auto ambient = tendril::sensors_read_ambient();

        ESP_LOGI(TAG, "Soil: %d%%, Temp: %.1f°F, Humidity: %.1f%%",
                 soil.moisture_pct,
                 ambient.valid ? ambient.temp_f : 0.0f,
                 ambient.valid ? ambient.humidity : 0.0f);

        // Update Zigbee attributes
        if (ambient.valid) {
            // ZCL temperature is in 0.01°C units
            float tempC = (ambient.temp_f - 32.0f) * 5.0f / 9.0f;
            int16_t zclTemp = (int16_t)(tempC * 100.0f);
            esp_zb_zcl_set_attribute_val(TENDRIL_ENDPOINT, ZB_TEMP_CLUSTER,
                                         ESP_ZB_ZCL_CLUSTER_SERVER_ROLE,
                                         ESP_ZB_ZCL_ATTR_TEMP_MEASUREMENT_VALUE_ID,
                                         &zclTemp, false);

            // ZCL humidity is in 0.01% units
            uint16_t zclHum = (uint16_t)(ambient.humidity * 100.0f);
            esp_zb_zcl_set_attribute_val(TENDRIL_ENDPOINT, ZB_HUMIDITY_CLUSTER,
                                         ESP_ZB_ZCL_CLUSTER_SERVER_ROLE,
                                         ESP_ZB_ZCL_ATTR_REL_HUMIDITY_MEASUREMENT_VALUE_ID,
                                         &zclHum, false);
        }

        // Sleep between reports
        vTaskDelay(pdMS_TO_TICKS(SLEEP_SECONDS * 1000));
    }
}

// ─── Zigbee Task ─────────────────────────────────────
static void esp_zb_task(void *arg) {
    esp_zb_cfg_t cfg = {
        .esp_zb_role = ESP_ZB_DEVICE_TYPE_ED,  // End Device (sleepy)
        .install_code_policy = false,
        .nwk_cfg = {
            .zed_cfg = {
                .ed_timeout = ESP_ZB_ED_AGING_TIMEOUT_64MIN,
                .keep_alive = 3000,
            },
        },
    };
    esp_zb_init(&cfg);

    // Create endpoint
    esp_zb_cluster_list_t *cluster_list = create_cluster_list();
    esp_zb_ep_list_t *ep_list = esp_zb_ep_list_create();
    esp_zb_endpoint_config_t ep_cfg = {
        .endpoint = TENDRIL_ENDPOINT,
        .app_profile_id = TENDRIL_PROFILE_ID,
        .app_device_id = TENDRIL_DEVICE_ID,
    };
    esp_zb_ep_list_add_ep(ep_list, cluster_list, ep_cfg);
    esp_zb_device_register(ep_list);

    esp_zb_set_primary_network_channel_set(ESP_ZB_TRANSCEIVER_ALL_CHANNELS_MASK);
    ESP_ERROR_CHECK(esp_zb_start(false));

    esp_zb_stack_main_loop();
}

// ─── Entry Point ─────────────────────────────────────
extern "C" void app_main(void) {
    esp_zb_platform_config_t platform_cfg = {};
    platform_cfg.radio_config.radio_mode = ZB_RADIO_MODE_NATIVE;
    platform_cfg.host_config.host_connection_mode = ZB_HOST_CONNECTION_MODE_NONE;

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_zb_platform_config(&platform_cfg));

    tendril::sensors_begin();

    xTaskCreate(esp_zb_task, "zigbee", 4096, NULL, 5, NULL);
    xTaskCreate(sensor_report_task, "sensors", 4096, NULL, 4, NULL);
}
