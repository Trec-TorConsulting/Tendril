#include "tendril_power.h"
#include <esp_sleep.h>
#include <driver/rtc_io.h>

namespace tendril {

Power::Power(uint8_t adc_pin, uint32_t r1, uint32_t r2)
    : _pin(adc_pin), _r1(r1), _r2(r2)
{
    _dividerRatio = static_cast<float>(_r1 + _r2) / static_cast<float>(_r2);
}

void Power::begin() {
    analogReadResolution(12);
    analogSetAttenuation(ADC_11db);  // 0-3.3V range
    pinMode(_pin, INPUT);
}

float Power::_readVoltage() {
    // Multi-sample for stability
    uint32_t sum = 0;
    for (int i = 0; i < 16; i++) {
        sum += analogRead(_pin);
        delayMicroseconds(100);
    }
    float adcAvg = static_cast<float>(sum) / 16.0f;
    float adcVoltage = (adcAvg / 4095.0f) * 3.3f;
    return adcVoltage * _dividerRatio;
}

uint8_t Power::_voltageToPct(float v) {
    if (v >= FULL_VOLTAGE) return 100;
    if (v <= EMPTY_VOLTAGE) return 0;
    // Piecewise linear approximation of Li-Ion discharge curve
    if (v >= 4.00f) return 90 + static_cast<uint8_t>((v - 4.00f) / (FULL_VOLTAGE - 4.00f) * 10.0f);
    if (v >= 3.80f) return 50 + static_cast<uint8_t>((v - 3.80f) / 0.20f * 40.0f);
    if (v >= 3.50f) return 20 + static_cast<uint8_t>((v - 3.50f) / 0.30f * 30.0f);
    if (v >= 3.30f) return 5  + static_cast<uint8_t>((v - 3.30f) / 0.20f * 15.0f);
    return static_cast<uint8_t>((v - EMPTY_VOLTAGE) / (3.30f - EMPTY_VOLTAGE) * 5.0f);
}

BatteryStatus Power::read() {
    float v = _readVoltage();
    uint8_t pct = _voltageToPct(v);
    return BatteryStatus{
        .voltage  = v,
        .percent  = pct,
        .low      = v < LOW_THRESHOLD,
        .critical = v < CRITICAL_THRESH,
    };
}

void Power::deepSleep(uint32_t seconds) {
    if (seconds > 0) {
        esp_sleep_enable_timer_wakeup(static_cast<uint64_t>(seconds) * 1000000ULL);
    }
    Serial.printf("[power] Sleeping for %u seconds\n", seconds);
    Serial.flush();
    esp_deep_sleep_start();
    // Never reaches here
    while (true) {}
}

void Power::deepSleep(uint32_t seconds, gpio_num_t wake_pin) {
    if (seconds > 0) {
        esp_sleep_enable_timer_wakeup(static_cast<uint64_t>(seconds) * 1000000ULL);
    }
    rtc_gpio_pullup_en(wake_pin);
    esp_sleep_enable_ext0_wakeup(wake_pin, 0);  // Wake on LOW
    Serial.printf("[power] Sleeping for %u seconds (ext0 on GPIO %d)\n", seconds, wake_pin);
    Serial.flush();
    esp_deep_sleep_start();
    while (true) {}
}

const char* Power::wakeReason() {
    switch (esp_sleep_get_wakeup_cause()) {
        case ESP_SLEEP_WAKEUP_TIMER:     return "timer";
        case ESP_SLEEP_WAKEUP_EXT0:      return "ext0_gpio";
        case ESP_SLEEP_WAKEUP_EXT1:      return "ext1_gpio";
        case ESP_SLEEP_WAKEUP_TOUCHPAD:  return "touchpad";
        case ESP_SLEEP_WAKEUP_ULP:       return "ulp";
        default:                         return "power_on";
    }
}

} // namespace tendril
