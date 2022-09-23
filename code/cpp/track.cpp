#include "track.h"

#include "hardware/clocks.h"

#include "pico/stdlib.h"

Track::Track(const int enGpio, const std::array<int, 2> &channelGpios, const float freq,
             const unsigned short lowest_spin_duty)
    : enGpio(enGpio), channelGpios(channelGpios), freq(freq), lowest_spin_duty(lowest_spin_duty) {

    gpio_set_function(enGpio, GPIO_FUNC_PWM);
    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, clock_get_hz(clk_sys) / freq);
    pwm_init(pwm_gpio_to_slice_num(enGpio), &config, true);
    pwm_set_gpio_level(enGpio, 0);

    for (const auto &chanGpio : channelGpios) {
        gpio_init(chanGpio);
        gpio_set_dir(chanGpio, GPIO_OUT);
    }
}

void Track::setPower(const float power) {
    if (power == 0)
        pwm_set_gpio_level(enGpio, 0);
    else
        pwm_set_gpio_level(
            enGpio, int(lowest_spin_duty + power / 100.f * (maxDutyCycle - lowest_spin_duty)));
}

void Track::brake() {
    setPower(100);
    for (const auto &chanGpio : channelGpios)
        gpio_put(chanGpio, 0);
}

void Track::forward(const float *power) {
    gpio_put(channelGpios.at(0), 1);
    gpio_put(channelGpios.at(1), 0);
    if (power != nullptr)
        setPower(*power);
}

void Track::backward(const float *power) {
    gpio_put(channelGpios.at(0), 0);
    gpio_put(channelGpios.at(1), 1);
    if (power != nullptr)
        setPower(*power);
}
