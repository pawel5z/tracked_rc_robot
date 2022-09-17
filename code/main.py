from machine import Pin, PWM, UART


class Track:
    """Class controlling a track with pair of L293 channels.
    """
    MAX_DUTY_CYCLE = 65535

    def __init__(self, enable: int, channels, freq: int, lowest_spin_duty: int = None):
        """Initialize Track object.

        Args:
            enable (PWM): Pin number with PWM capability.
            channels (List[int]): List of two pin numbers connected to L293 channels.
            The first one refers to forward channel, the second one to backward.
            freq (int): PWM frequency.
            lowest_spin_duty (int, optional): Integer in range 0 to 65535.
            The lowest duty cycle making track spin. Defaults to None.

        Raises:
            ValueError: If given incorrect argument.
        """
        self.enable = PWM(Pin(enable))
        self.enable.freq(freq)
        self.enable.duty_u16(0)
        if len(channels) != 2:
            raise ValueError(f"Incorrent number of channels: {2}.")
        self.channels = [Pin(channels[0], Pin.OUT), Pin(channels[1], Pin.OUT)]
        if lowest_spin_duty is not None and lowest_spin_duty < 0 or lowest_spin_duty > 65535:
            raise ValueError(
                f"Incorrect lowest_spin_duty value: {lowest_spin_duty}.")
        self.lowest_spin_duty = lowest_spin_duty

    def set_power(self, power: float):
        """Set track's power in range [0, 100]%.

        Args:
            duty (float): Number in range [0, 100].
        """
        if self.lowest_spin_duty is None or power == 0:
            self.enable.duty_u16(int(power / 100 * Track.MAX_DUTY_CYCLE))
        else:
            self.enable.duty_u16(int(self.lowest_spin_duty + power /
                                 100 * (Track.MAX_DUTY_CYCLE - self.lowest_spin_duty)))

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
    """Class containing Dabble gamepad specific values and methods.
    https://thestempedia.com/docs/dabble/game-pad-module/
    """
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

    RIGHT_ANGLE_OFFSET = 6

    MAX_RADIUS = 7
    RADIUS_MASK = 0b111
    DIR_MASK = ~RADIUS_MASK

    @staticmethod
    def get_joystick_radius(joystick: int) -> int:
        """Get radius from joystick byte of the packet.

        Args:
            joystick (int): Joystick byte of the packet.

        Returns:
            int: Radius input.
        """
        return joystick & DabbleGamepad.RADIUS_MASK

    @staticmethod
    def get_joystick_dir(joystick: int) -> int:
        """Get direction from joystick byte of the packet.

        Args:
            joystick (int): Joystick byte of the packet.

        Returns:
            int: Number coding direction. From 0 to 23. 15-degree parts of 360 degree angle measured counter-clockwise from right.
        """
        return (joystick & DabbleGamepad.DIR_MASK) >> 3


def handle_button(button: int, track_left: Track, track_right: Track):
    """Handle button press.

    Args:
        button (int): Button bitmask.
        track_left (Track): Left track.
        track_right (Track): Right track.
    """
    if button & DabbleGamepad.SQUARE:
        track_left.fast_stop()
        track_right.fast_stop()


def handle_joystick(joystick: int, track_left: Track, track_right: Track):
    """Handle joystick input.

    Args:
        joystick (int): Joystick byte of the packet.
        track_left (Track): Left track.
        track_right (Track): Right track.
    """
    radius = DabbleGamepad.get_joystick_radius(joystick)
    if radius == 0:
        track_left.set_power(0)
        track_right.set_power(0)
        return

    direction = DabbleGamepad.get_joystick_dir(joystick)

    left_power = 100
    if direction >= DabbleGamepad.DEG_90 and direction < DabbleGamepad.DEG_180:
        track_left.forward()
        left_power *= (DabbleGamepad.DEG_180 - direction) / \
            DabbleGamepad.RIGHT_ANGLE_OFFSET
    elif direction <= DabbleGamepad.DEG_270 and direction > DabbleGamepad.DEG_180:
        track_left.backward()
        left_power *= (direction - DabbleGamepad.DEG_180) / \
            DabbleGamepad.RIGHT_ANGLE_OFFSET
    elif direction == DabbleGamepad.DEG_180:
        track_left.backward()
    elif direction < DabbleGamepad.DEG_90:
        track_left.forward()
    elif direction > DabbleGamepad.DEG_270:
        track_left.backward()

    right_power = 100
    if direction <= DabbleGamepad.DEG_90 and direction > 0:
        track_right.forward()
        right_power *= direction / DabbleGamepad.RIGHT_ANGLE_OFFSET
    elif direction >= DabbleGamepad.DEG_270:
        track_right.backward()
        right_power *= (DabbleGamepad.DIRS_CNT - direction) / \
            DabbleGamepad.RIGHT_ANGLE_OFFSET
    elif direction == DabbleGamepad.DEG_0:
        track_right.backward()
    elif direction <= DabbleGamepad.DEG_180:
        track_right.forward()
    elif direction < DabbleGamepad.DEG_270:
        track_right.backward()

    radius_mul = radius / DabbleGamepad.MAX_RADIUS
    track_left.set_power(left_power * radius_mul)
    track_right.set_power(right_power * radius_mul)


led = Pin(25, Pin.OUT, value=1)
led(1)

TRACK_MOTOR_PWM_FREQ = 5000
LOWEST_SPIN_DUTY = 44032
track_left = Track(21, [19, 18], TRACK_MOTOR_PWM_FREQ, LOWEST_SPIN_DUTY)
track_right = Track(20, [17, 16], TRACK_MOTOR_PWM_FREQ, LOWEST_SPIN_DUTY)

bt_uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9),
               timeout=1000)

packet = bytes()
while True:
    byte = bt_uart.read(1)
    if byte == b'\x00' and len(packet) == 7 and packet[:5] == DabbleGamepad.GAMEPAD_MAGIC:
        handle_joystick(packet[6], track_left, track_right)
        handle_button(packet[5], track_left, track_right)
        packet = bytes()
    elif byte is not None:
        packet = (packet + byte)[-7:]
