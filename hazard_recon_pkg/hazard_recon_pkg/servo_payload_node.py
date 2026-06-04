#!/usr/bin/env python3
"""
ROS2 node: Servo payload drop controller.
Subscribes to /hazard_detected and triggers the appropriate servo.

  green triangle → Servo 1 (GPIO 12) drops green puck
  red trangle    → Servo 2 (GPIO 13) drops red puck
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import RPi.GPIO as GPIO
import time
import threading

# GPIO pins
SERVO1_PIN = 12   # green puck
SERVO2_PIN = 13   # red puck
FREQ       = 50   # 50Hz PWM

# Duty cycles — tune once servos are mounted in payload bay
SERVO1_HOLD = 2.5
SERVO1_DROP = 7.5
SERVO2_HOLD = 12.5
SERVO2_DROP = 7.5

DROP_DURATION = 1.0  # seconds to hold drop position
COOLDOWN      = 3.0  # seconds before servo can fire again


class ServoPayloadNode(Node):
    def __init__(self):
        super().__init__('servo_payload_node')

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SERVO1_PIN, GPIO.OUT)
        GPIO.setup(SERVO2_PIN, GPIO.OUT)
        self.pwm1 = GPIO.PWM(SERVO1_PIN, FREQ)
        self.pwm2 = GPIO.PWM(SERVO2_PIN, FREQ)
        self.pwm1.start(0)
        self.pwm2.start(0)

        # Move both to hold on startup
        self._set_angle(self.pwm1, SERVO1_HOLD)
        self._set_angle(self.pwm2, SERVO2_HOLD)

        self.servo1_lock = threading.Lock()
        self.servo2_lock = threading.Lock()

        self.sub = self.create_subscription(
            String, '/hazard_detected', self.detection_callback, 10)
        self.get_logger().info('Servo payload node ready.')

    def _set_angle(self, pwm, duty):
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(0)

    def _drop_servo1(self):
        self.get_logger().info('Servo1 (green): DROP')
        self._set_angle(self.pwm1, SERVO1_DROP)
        time.sleep(DROP_DURATION)
        self._set_angle(self.pwm1, SERVO1_HOLD)
        self.get_logger().info('Servo1 (green): returned to hold')
        time.sleep(COOLDOWN)
        self.servo1_lock.release()

    def _drop_servo2(self):
        self.get_logger().info('Servo2 (red): DROP')
        self._set_angle(self.pwm2, SERVO2_DROP)
        time.sleep(DROP_DURATION)
        self._set_angle(self.pwm2, SERVO2_HOLD)
        self.get_logger().info('Servo2 (red): returned to hold')
        time.sleep(COOLDOWN)
        self.servo2_lock.release()

    def detection_callback(self, msg: String):
        label = msg.data

        if label == 'green triangle' and self.servo1_lock.acquire(blocking=False):
            threading.Thread(target=self._drop_servo1, daemon=True).start()

        elif label == 'red trangle' and self.servo2_lock.acquire(blocking=False):
            threading.Thread(target=self._drop_servo2, daemon=True).start()

    def destroy_node(self):
        self.pwm1.stop()
        self.pwm2.stop()
        self.pwm1 = None
        self.pwm2 = None
        GPIO.cleanup()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = ServoPayloadNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
