#include "dabble.h"
#include "track.h"

#include "hardware/uart.h"

#include "pico/stdlib.h"

#include <deque>

/**
 * @brief Handle button press.
 *
 * @param button Button bitmask.
 * @param trackLeft
 * @param trackRight
 */
void handleButton(char button, Track &trackLeft, Track &trackRight) {
    if (button & dabble_gamepad::square) {
        trackLeft.brake();
        trackRight.brake();
    }
}

/**
 * @brief Handle joystick input.
 *
 * @param joystick
 * @param trackLeft
 * @param trackRight
 */
void handleJoystick(char joystick, Track &trackLeft, Track &trackRight) {
    int radius = dabble_gamepad::getJoystickRadius(joystick);
    if (radius == 0) {
        trackLeft.setPower(0);
        trackRight.setPower(0);
        return;
    }

    int direction = dabble_gamepad::getJoystickDir(joystick);

    float leftPower = 100;
    if (direction >= dabble_gamepad::deg90 && direction < dabble_gamepad::deg180) { // up, up/left
        trackLeft.forward();
        leftPower *= (dabble_gamepad::deg180 - direction) / float(dabble_gamepad::rightAngleOffset);
    } else if (direction <= dabble_gamepad::deg270 &&
               direction > dabble_gamepad::deg180) { // down, down/left
        trackLeft.backward();
        leftPower *= (direction - dabble_gamepad::deg180) / float(dabble_gamepad::rightAngleOffset);
    } else if (direction == dabble_gamepad::deg180) // left
        trackLeft.backward();
    else if (direction < dabble_gamepad::deg90) // up/right, right
        trackLeft.forward();
    else if (direction > dabble_gamepad::deg270) // down/right
        trackLeft.backward();

    float rightPower = 100;
    if (direction <= dabble_gamepad::deg90 and direction > 0) { // up, up/right
        trackRight.forward();
        rightPower *= direction / float(dabble_gamepad::rightAngleOffset);
    } else if (direction >= dabble_gamepad::deg270) { // down, down/right
        trackRight.backward();
        rightPower *=
            (dabble_gamepad::dirsCnt - direction) / float(dabble_gamepad::rightAngleOffset);
    } else if (direction == dabble_gamepad::deg0) // right
        trackRight.backward();
    else if (direction <= dabble_gamepad::deg180) // left, up/left
        trackRight.forward();
    else if (direction < dabble_gamepad::deg270) // down/left
        trackRight.backward();

    float radiusMul = radius / float(dabble_gamepad::maxRadius);
    trackLeft.setPower(leftPower * radiusMul);
    trackRight.setPower(rightPower * radiusMul);
}

int main() {
    // Set on-board led to constant flashing.
    gpio_init(PICO_DEFAULT_LED_PIN);
    gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
    gpio_put(PICO_DEFAULT_LED_PIN, 1);

    // Set up tracks' controls.
    const int trackMotorPwmFreq = 5000; // Maximum recommended frequency for L293.
    const int lowestSpinDuty = 832;     // Obtained from testing.
    Track trackLeft(21, {19, 18}, trackMotorPwmFreq, lowestSpinDuty);
    Track trackRight(20, {17, 16}, trackMotorPwmFreq, lowestSpinDuty);

    // Set up UART communication with bluetooth module.
#define BT_UART uart1
#define BT_UART_TX_PIN 8
#define BT_UART_RX_PIN 9
    uart_init(BT_UART, 9600);
    uart_set_format(BT_UART, 8, 1, UART_PARITY_NONE);
    gpio_set_function(BT_UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(BT_UART_RX_PIN, GPIO_FUNC_UART);

    std::deque<char> packet;

    while (true) {
        char byte = uart_getc(BT_UART);

        if (byte == 0x00 && packet.size() == 7 &&
            std::deque<char>(packet.begin(), packet.begin() + 5) ==
                dabble_gamepad::joystickGamepadMagic) {
            handleJoystick(packet.at(6), trackLeft, trackRight);
            handleButton(packet.at(5), trackLeft, trackRight);
        }

        packet.push_back(byte);
        if (packet.size() == 8)
            packet.pop_front();
    }
}
