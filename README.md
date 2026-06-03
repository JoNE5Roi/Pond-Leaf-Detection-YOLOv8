# 🍃 Automatic Pond Leaf Detection System

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)

A real-time AI vision system designed to detect and monitor falling leaves on a pond surface. This project utilizes a GoPro camera for high-quality video capture, YOLOv8 for object detection, and integrates with LINE Notify for smart alerting.

## ✨ Key Features

* **Real-time Object Detection:** Leverages **YOLOv8** to identify specific types of leaves commonly found near the pond (e.g., Mango, Tamarind, and Yellow Elder leaves).
* **Smart Notification System (LINE Notify):**
  * **Alert Mode:** Sends immediate notifications via LINE when large leaves are detected on the water surface.
  * **Logging Mode:** Silently records and logs the presence of small leaves without spamming notifications.
* **Wireless Camera Integration:** Uses a **GoPro** as the primary image sensor, streaming data wirelessly to the processing unit.
* **Custom Network Architecture:** Implemented **Static Routing** and **IP Forwarding** to establish seamless communication between the GoPro, a Raspberry Pi, and the main processing PC.

## 🛠️ System Architecture & Hardware

1. **Camera Input:** GoPro (Wireless Stream)
2. **Network Hub:** Raspberry Pi (Handles IP Forwarding and routing from GoPro to PC)
3. **Processing Unit:** PC (Runs Python, OpenCV, and the YOLOv8 inference engine)
4. **Output/Alert:** LINE Messaging API

## 🚀 Getting Started

### Prerequisites
* Python 3.8+
* Ultralytics (YOLOv8)
* OpenCV
* LINE Notify Token

### Installation
1. Clone this repository:
   ```bash
   git clone [https://github.com/JoNE5Roi/Pond-Leaf-Detection-YOLOv8.git](https://github.com/JoNE5Roi/Pond-Leaf-Detection-YOLOv8.git)