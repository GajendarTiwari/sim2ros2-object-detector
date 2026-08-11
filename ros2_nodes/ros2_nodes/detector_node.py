#!/usr/bin/env python3
"""
detector_node.py

A ROS2 node that:
  1. Subscribes to "/camera/image_raw" (published by image_publisher.py)
  2. Runs a YOLO object detector on each incoming frame
  3. Prints what it found and publishes a short text summary
     to the "/detections" topic

This is the "ML brain" of the pipeline - the model itself was trained
separately in Google Colab and just gets loaded here.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
from ultralytics import YOLO

MODEL_PATH = "/workspace/best.pt"


class DetectorNode(Node):
    def __init__(self):
        super().__init__("detector_node")
        self.bridge = CvBridge()

        self.get_logger().info(f"Loading model from {MODEL_PATH} ...")
        self.model = YOLO(MODEL_PATH)
        self.get_logger().info("Model loaded.")

        self.subscription = self.create_subscription(
            Image, "/camera/image_raw", self.image_callback, 10
        )
        self.detections_pub = self.create_publisher(String, "/detections", 10)

        self.get_logger().info("Detector ready, waiting for images...")

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = self.model(frame, verbose=False)

        names = results[0].names
        boxes = results[0].boxes

        found = []
        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            label = names[class_id]
            found.append(f"{label} ({confidence:.2f})")

        summary = ", ".join(found) if found else "nothing detected"
        self.get_logger().info(f"Detections: {summary}")

        out_msg = String()
        out_msg.data = summary
        self.detections_pub.publish(out_msg)


def main():
    rclpy.init()
    node = DetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
