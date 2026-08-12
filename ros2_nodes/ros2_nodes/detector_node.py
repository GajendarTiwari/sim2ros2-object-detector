import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from ultralytics import YOLO

MODEL_PATH = "/workspace/best.pt"


class DetectorNode(Node):
    def __init__(self):
        super().__init__("detector_node")

        self.get_logger().info(f"Loading model from {MODEL_PATH} ...")
        self.model = YOLO(MODEL_PATH)
        self.get_logger().info("Model loaded.")

        self.subscription = self.create_subscription(
            Image, "/camera/image_raw", self.image_callback, 10
        )
        self.detections_pub = self.create_publisher(String, "/detections", 10)

        self.get_logger().info("Detector ready, waiting for images...")

    def image_callback(self, msg):
        frame = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, 3)

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

