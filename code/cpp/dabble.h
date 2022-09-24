#pragma once

#include <deque>

/**
 * @brief Namespace containing Dabble gamepad specific values and helper functions.
 * https://thestempedia.com/docs/dabble/game-pad-module/
 */
namespace dabble_gamepad {
const std::deque<char> joystickGamepadMagic = {0xff, 0x01, 0x02, 0x01, 0x02};

const char start = 0x1;
const char select = 0x2;
const char cross = 0x10;
const char triangle = 0x04;
const char circle = 0x08;
const char square = 0x20;

const char dirsCnt = 24;
const char dirsInQuaterCnt = 7;
const char zeroAngle = 0;
const char deg0 = zeroAngle;
const char rightAngle = 6;
const char deg90 = rightAngle;
const char straightAngle = 12;
const char deg180 = straightAngle;
const char deg270 = 18;
const char fullAngle = zeroAngle;
const char deg360 = zeroAngle;

const char rightAngleOffset = 6;

const char maxRadius = 7;
const char radiusMask = 0b111;
const char dirMask = ~radiusMask;

/**
 * @brief Get radius from joystick byte of the packet.
 *
 * @param joystick Joystick byte of the packet.
 * @return Radius input.
 */
int getJoystickRadius(const char joystick);

/**
 * @brief Get direction from joystick byte of the packet.
 *
 * @param joystick Joystick byte of the packet.
 * @return Number from range 0 to 23, encoding direction. 15-degree parts of 360 degree angle
 * measured counter-clockwise from the right.
 */
int getJoystickDir(const char joystick);
};
