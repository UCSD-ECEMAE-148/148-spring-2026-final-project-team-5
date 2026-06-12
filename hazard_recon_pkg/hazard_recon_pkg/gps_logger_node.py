#!/usr/bin/env python3
"""
ROS2 node: GPS logger.
Subscribes to /fix (sensor_msgs/NavSatFix) from nmea_navsat_driver.
Logs GPS coordinates to a CSV file when a hazard is detected.
"""

import csv
import os
from datetime import datetime

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from std_msgs.msg import String

LOG_FILE = '/home/projects/gps_log.csv'
LOG_TRIGGERS = {'red trangle', 'red triangle', 'green triangle', 'blue triangle'}


class GpsLoggerNode(Node):
    def __init__(self):
        super().__init__('gps_logger_node')

        self.lat = None
        self.lon = None
        self.fix_valid = False

        # Subscribe to /fix from nmea_navsat_driver
        self.fix_sub = self.create_subscription(
            NavSatFix, '/fix', self.fix_callback, 10)

        # Subscribe to hazard detections
        self.hazard_sub = self.create_subscription(
            String, '/hazard_detected', self.detection_callback, 10)

        # Set up CSV
        write_header = not os.path.exists(LOG_FILE)
        self.csv_file = open(LOG_FILE, 'a', newline='')
        self.writer = csv.writer(self.csv_file)
        if write_header:
            self.writer.writerow(['timestamp', 'hazard', 'latitude', 'longitude'])
            self.csv_file.flush()

        self.get_logger().info(f'GPS logger ready. Logging to {LOG_FILE}')

    def fix_callback(self, msg: NavSatFix):
        # status 0 = fix, 1 = SBAS fix, 2 = GBAS fix; -1 = no fix
        if msg.status.status >= 0 and msg.latitude == msg.latitude:  # nan check
            self.lat = msg.latitude
            self.lon = msg.longitude
            self.fix_valid = True
        else:
            self.fix_valid = False

    def detection_callback(self, msg: String):
        label = msg.data.strip().lower()
        if label not in LOG_TRIGGERS:
            return

        timestamp = datetime.now().isoformat()

        if self.fix_valid and self.lat is not None:
            self.writer.writerow([timestamp, label, self.lat, self.lon])
            self.get_logger().info(
                f'Logged: {label} @ ({self.lat:.6f}, {self.lon:.6f})')
        else:
            self.writer.writerow([timestamp, label, 'NO_FIX', 'NO_FIX'])
            self.get_logger().warn(
                f'Logged: {label} but GPS has no fix!')

        self.csv_file.flush()

    def destroy_node(self):
        self.csv_file.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GpsLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
