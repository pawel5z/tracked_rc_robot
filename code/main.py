from machine import Pin, PWM, UART
from binascii import hexlify


class Track:
    """Class controlling a track with pair of L293 channels.
    """
    MAX_DUTY_CYCLE = 65535

    def __init__(self, enable: int, channels, freq: int):
        """Initialize Track object.

        Args:
            enable (PWM): Pin number with PWM capability.
            channels (List[int]): List of two pin numbers connected to L293 channels.
            The first one refers to forward channel, the second one to backward.
            freq (int): PWM frequency.
        """
        self.enable = PWM(Pin(enable))
        self.enable.freq(freq)
        self.enable.duty_u16(0)
        if len(channels) != 2:
            raise ValueError(f"Incorrent number of channels: {2}.")
        self.channels = [Pin(channels[0], Pin.OUT), Pin(channels[1], Pin.OUT)]

    def set_power(self, power: float):
        """Set track's power in range [0, 100]%.

        Args:
            duty (float): Number in range [0, 100].
        """
        self.enable.duty_u16(int(power / 100 * Track.MAX_DUTY_CYCLE))

    def fast_stop(self):
        """Brake the track.
        """
        self.set_power(100)
        for chan in self.channels:
            chan(0)

    def forward(self, power: float = None):
        """Rotate track forward.

        Args:
            power (float, optional): Optional track's power to set. Defaults to None.
        """
        self.channels[0](1)
        self.channels[1](0)
        if power is not None:
            self.set_power(power)

    def backward(self, power: float = None):
        """Rotate track backward.

        Args:
            power (float, optional): Optional track's power to set. Defaults to None.
        """
        self.channels[0](0)
        self.channels[1](1)
        if power is not None:
            self.set_power(power)


class DabbleGamepad:
    GAMEPAD_MAGIC = b'\xff\x01\x02\x01\x02'

    START = 0x1
    SELECT = 0x2
    CROSS = 0x10
    TRIANGLE = 0x04
    CIRCLE = 0x08
    SQUARE = 0x20

    DIRS_CNT = 24
    DIRS_IN_QT_CNT = 7
    ZERO_ANGLE = 0
    DEG_0 = ZERO_ANGLE
    RIGHT_ANGLE = 6
    DEG_90 = RIGHT_ANGLE
    STRAIGHT_ANGLE = 12
    DEG_180 = STRAIGHT_ANGLE
    DEG_270 = 18
    FULL_ANGLE = 0
    DEG_360 = 0

    MAX_RADIUS = 7
    RADIUS_MASK = 0x3
    DIR_MASK = ~RADIUS_MASK

    @staticmethod
    def get_joystick_radius(joystick: int):
        return joystick & DabbleGamepad.RADIUS_MASK

    @staticmethod
    def get_joystick_dir(joystick: int):
        return joystick & DabbleGamepad.DIR_MASK >> 3


def handle_button(button: int, track_left: Track, track_right: Track):
    if button & DabbleGamepad.SQUARE:
        track_left.fast_stop()
        track_right.fast_stop()


def handle_joystick(joystick: int, track_left: Track, track_right: Track):
    radius = DabbleGamepad.get_joystick_radius(joystick)
    if radius == 0:
        track_left.set_power(0)
        track_left.set_power(0)
        return

    dir = DabbleGamepad.get_joystick_dir(joystick)

    left_power = 100
    if dir >= DabbleGamepad.DEG_90 and dir < DabbleGamepad.DEG_180:
        track_left.forward()
        left_power *= DabbleGamepad.DEG_180 - dir
    elif dir <= DabbleGamepad.DEG_270 and dir > DabbleGamepad.DEG_180:
        track_left.backward()
        left_power *= dir - DabbleGamepad.DEG_180
    elif dir == DabbleGamepad.DEG_180:
        track_left.backward()
    else:
        track_left.forward()

    right_power = 100
    if dir <= DabbleGamepad.DEG_90 and dir > 0:
        right_power *= dir / DabbleGamepad.DIRS_IN_QT_CNT
    elif dir >= DabbleGamepad.DEG_270:
        right_power *= DabbleGamepad.DIRS_CNT - dir
    elif dir == DabbleGamepad.DEG_0:
        track_right.backward()
    else:
        track_right.forward()

    radius_mul = radius / DabbleGamepad.MAX_RADIUS
    track_left.set_power(left_power * radius_mul)
    track_right.set_power(right_power * radius_mul)


led = Pin(25, Pin.OUT, value=1)
led(1)

TRACK_MOTOR_PWM_FREQ = 5000
track_left = Track(21, [19, 18], TRACK_MOTOR_PWM_FREQ)
track_right = Track(20, [17, 16], TRACK_MOTOR_PWM_FREQ)

bt_uart = UART(1, baudrate=460800, tx=Pin(8), rx=Pin(9),
               timeout=1000, timeout_char=100)

packet = bytes()
logfile = open("log.txt", "w")
while True:
    byte = bt_uart.read(1)
    if byte == b'\x00' and len(packet) == 7 and packet[:5] == DabbleGamepad.GAMEPAD_MAGIC:
        handle_joystick(packet[6], track_left, track_right)
        handle_button(packet[5], track_left, track_right)
        packet = bytes()
    elif byte is not None:
        logfile.write(f"{hexlify(byte, ' ')}\n")
        logfile.flush()
        packet = (packet + byte)[-7:]