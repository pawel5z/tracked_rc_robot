from machine import Pin, PWM, UART


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
        self.enable = PWM(enable)
        self.enable.freq(freq)
        self.enable.duty_u16(0)
        if len(channels) != 2:
            raise ValueError(f"Incorrent number of channels: {2}")
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


TRACK_MOTOR_PWM_FREQ = 5000
track_left = Track(21, [19, 18], TRACK_MOTOR_PWM_FREQ)
track_right = Track(20, [17, 16], TRACK_MOTOR_PWM_FREQ)

bt_uart = UART(1, baudrate=460800, tx=Pin(8), rx=Pin(9),
               timeout=1000, timeout_char=100)


while True:
    ...
