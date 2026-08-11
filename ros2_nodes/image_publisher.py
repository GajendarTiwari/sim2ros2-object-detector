#!/usr/bin/env python3
"""
image_publisher.py

A simple ROS2 node that acts like a fake camera.
It reads image files from a folder, one at a time, and publishes
them to the "/camera/image_raw" topic every few seconds.

Think of this as standing in for a real robot's camera - later you
could swap this out for an actual webcam or an Isaac Sim camera feed
without touching the detector node at all.
"""
import os
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

IMAGE_FOLDER = "/workspace/sample_images"
PUBLISH_EVERY_SECONDS = 3.0


class ImagePublisher(Node):
    def __init__(self):
        super().__init__("image_publisher")
        self.publisher_ = self.create_publisher(Image, "/camera/image_raw", 10)
        self.bridge = CvBridge()

        self.image_files = sorted([
            f for f in os.listdir(IMAGE_FOLDER)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        if not self.image_files:
            self.get_logger().error(f"No images found in {IMAGE_FOLDER}")
        else:
            self.get_logger().info(f"Found {len(self.image_files)} images to publish")

        self.index = 0
        self.timer = self.create_timer(PUBLISH_EVERY_SECONDS, self.publish_next_image)

    def publish_next_image(self):
        if not self.image_files:
            return

        filename = self.image_files[self.index % len(self.image_files)]
        path = os.path.join(IMAGE_FOLDER, filename)
        frame = cv2.imread(path)

        if frame is None:
            self.get_logger().warn(f"Could not read {path}, skipping")
            self.index += 1
            return

        msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published: {filename}")
        self.index += 1


def main():
    rclpy.init()
    node = ImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
