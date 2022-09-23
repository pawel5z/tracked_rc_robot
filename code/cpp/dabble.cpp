#include "dabble.h"

int dabble_gamepad::getJoystickRadius(const char joystick) { return joystick & radiusMask; }

int dabble_gamepad::getJoystickDir(const char joystick) { return (joystick & dirMask) >> 3; }
