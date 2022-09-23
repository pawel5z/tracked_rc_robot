#pragma once

#include <deque>
#include <string>

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

int getJoystickRadius(const char joystick);
int getJoystickDir(const char joystick);
};
