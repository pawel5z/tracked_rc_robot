#pragma once

#include "hardware/pwm.h"

#include <array>

/**
 * @brief Class controlling a track with a pair of L293 channels.
 */
class Track {
public:
    static const unsigned short maxDutyCycle = 1024;

    /**
     * @brief Construct a new Track object.
     *
     * @param enGpio Pin number with PWM capability.
     * @param channelGpios Array of two pin numbers connected to L293 channels. The first one refers
     * to forward channel, the second one to backward.
     * @param freq PWM frequency.
     * @param lowest_spin_duty Integer in range 0 to 1024. The lowest duty cycle making track spin.
     */
    Track(const int enGpio, const std::array<int, 2> &channelGpios, const float freq,
          const unsigned short lowest_spin_duty = 0);

    /**
     * @brief Set track's power in range [0, 100]%.
     *
     * @param power Number in range [0, 100]%.
     */
    void setPower(const float power);

    /**
     * @brief Brake the track.
     */
    void brake();

    /**
     * @brief Set track's rotation to forward.
     *
     * @param power Optional track's power to set.
     */
    void forward(const float *power = nullptr);

    /**
     * @brief Set track's rotation to backward.
     *
     * @param power Optional track's power to set.
     */
    void backward(const float *power = nullptr);

private:
    int enGpio;
    std::array<int, 2> channelGpios;
    float freq;
    unsigned short lowest_spin_duty;
};
