#pragma once

#include "hardware/pwm.h"

#include <array>

class Track {
public:
    static const int unsigned short maxDutyCycle = 65535;

    Track(const int enGpio, const std::array<int, 2> &channelGpios, const float freq,
          const unsigned short lowest_spin_duty = 0);
    void setPower(const float power);
    void brake();
    void forward(const float *power = nullptr);
    void backward(const float *power = nullptr);

private:
    int enGpio;
    std::array<int, 2> channelGpios;
    float freq;
    unsigned short lowest_spin_duty;
};
