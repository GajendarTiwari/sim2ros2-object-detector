# Sim-to-ROS2 Object Detector

A small end-to-end pipeline that trains a lightweight object detector on
synthetic-style data and deploys it as a live ROS2 node — the same basic
pattern used in real robotics/ML pipelines, built with fully free tools.

## Pipeline

1. **Train** — A YOLOv8-nano model is fine-tuned on a small labeled image
   set in Google Colab (free GPU).
2. **Simulate a camera feed** — A ROS2 publisher node (`image_publisher.py`)
   reads images from disk and streams them to a `/camera/image_raw` topic,
   standing in for a live camera or simulated sensor.
3. **Detect** — A ROS2 subscriber node (`detector_node.py`) loads the
   trained model, runs inference on every incoming frame, prints the
   detections, and republishes them as text on `/detections`.

## Why not live NVIDIA Isaac Sim?

Isaac Sim is the standard tool for generating synthetic training data and
simulating full robot/sensor pipelines before deploying to ROS2. It was
intentionally left out of this build because it only runs on Windows or
Linux with a supported NVIDIA RTX GPU — it does not run on macOS or in any
free cloud tier. On a machine that meets those requirements, the natural
next step for this project would be:

- Replace the static `sample_images/` folder with a live camera feed
  published directly from an Isaac Sim scene via its built-in ROS2 bridge.
- Use Isaac Sim's Replicator tool to auto-generate a larger, labeled
  synthetic dataset (with domain randomization) instead of a small static
  one, before the Colab training step.

## Tech stack

- **ROS2 Humble** (via Docker, so it runs identically on any OS)
- **Ultralytics YOLOv8** for training and inference
- **OpenCV** / **cv_bridge** for image handling between OpenCV and ROS2
- **Google Colab** (free T4 GPU) for training

## Running it

See the setup steps in the project write-up. Short version:

\`\`\`bash
# Pull the ROS2 image
docker pull osrf/ros:humble-desktop

# Run the container with the project folder mounted
docker run -it --rm -v $(pwd):/workspace osrf/ros:humble-desktop bash

# Inside the container
apt-get update && apt-get install -y ros-humble-cv-bridge python3-pip
pip install -r /workspace/requirements.txt

# Terminal 1
python3 /workspace/ros2_nodes/detector_node.py

# Terminal 2 (docker exec into the same container)
python3 /workspace/ros2_nodes/image_publisher.py
\`\`\`

## Files

\`\`\`
.
├── best.pt                     # trained model weights (from Colab)
├── sample_images/               # test images used as a fake camera feed
├── ros2_nodes/
│   ├── image_publisher.py
│   └── detector_node.py
├── requirements.txt
└── README.md
\`\`\`
