#pragma once
/// @file tendril_power.h
/// Battery monitoring, deep sleep, and low-power management for Tendril kits.

#include <Arduino.h>

namespace tendril {

struct BatteryStatus {
    float voltage;      // Cell voltage (V)
    uint8_t percent;    // Estimated SoC 0-100
    bool low;           // True when below LOW_THRESHOLD
    bool critical;      // True when below CRITICAL_THRESHOLD
};

class Power {
public:
    /// @param adc_pin  ADC1 pin connected to the voltage divider midpoint
    /// @param r1       Top resistor of divider (ohms), connected to VBAT
    /// @param r2       Bottom resistor of divider (ohms), connected to GND
    Power(uint8_t adc_pin, uint32_t r1 = 100000, uint32_t r2 = 100000);

    /// Call once in setup(). Configures ADC attenuation and resolution.
    void begin();

    /// Read battery voltage and compute SoC.
    BatteryStatus read();

    /// Enter deep sleep for the given duration.  Wakes via RTC timer.
    /// @param seconds  Sleep duration in seconds (0 = indefinite, wake on ext0/ext1 only)
    [[noreturn]] void deepSleep(uint32_t seconds);

    /// Enter deep sleep, but wake early if a GPIO goes LOW (ext0 wakeup).
    /// Useful for a "factory reset" button.
    [[noreturn]] void deepSleep(uint32_t seconds, gpio_num_t wake_pin);

    /// Call at top of setup() to detect why we woke and log it.
    static const char* wakeReason();

    // Voltage thresholds (18650 Li-Ion)
    static constexpr float FULL_VOLTAGE     = 4.15f;
    static constexpr float EMPTY_VOLTAGE    = 3.00f;
    static constexpr float LOW_THRESHOLD    = 3.30f;
    static constexpr float CRITICAL_THRESH  = 3.10f;

private:
    uint8_t  _pin;
    uint32_t _r1;
    uint32_t _r2;
    float    _dividerRatio;

    float _readVoltage();
    uint8_t _voltageToPct(float v);
};

} // namespace tendril
