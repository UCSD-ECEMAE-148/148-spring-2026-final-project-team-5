import pygame
import time
from pyvesc import VESC

SERIAL_PORT = '/dev/ttyACM1'
STEERING_OFFSET = 0.5
STEERING_SCALE = 0.4
MAX_RPM = 4000

pygame.init()
pygame.joystick.init()
js = pygame.joystick.Joystick(0)
js.init()
print(f"Joystick: {js.get_name()}")

with VESC(SERIAL_PORT) as v:
    print("VESC connected. Left stick = steer, Right stick up/down = throttle. Ctrl+C to quit.")
    try:
        while True:
            pygame.event.pump()
            steering = js.get_axis(0)   # left stick X
            throttle = -js.get_axis(4)  # right stick Y, negated so up = forward

            servo = STEERING_OFFSET + STEERING_SCALE * steering
            servo = max(0.1, min(0.9, servo))  # clamp to safe range

            rpm = int(MAX_RPM * throttle)

            v.set_servo(servo)
            v.set_rpm(rpm)
            time.sleep(0.05)

    except KeyboardInterrupt:
        v.set_rpm(0)
        v.set_servo(STEERING_OFFSET)
        print("Stopped.")
