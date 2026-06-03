import tkinter as tk
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk, ImageDraw
import requests
import json
import datetime
import time
import os
import numpy as np

from ultralytics import YOLO

# ==========================================
# ⚙️ System Settings
# ==========================================
CHANNEL_ACCESS_TOKEN = 'Say1Nz3rASSi0EGE0OxSa/fsMjlYdro7T1EHQPxjLzJqKlUFSEHlCjKfDs+0T8JrZPSILHXVCyBc9U81mZ/6ysKqnBFyGZaFhY/z4rEuxwEj8Kvxya8VWE/wNUWh24qQFAAGAMyVjcrNaZibauUFCQdB04t89/1O/w1cDnyilFU='
IMGBB_API_KEY = 'c588d5cdac0894cedbf5b2d024a77a94'

# อัปเดต Class ทั้งหมด (เพิ่ม Class 3)
CLASS_NAMES_EN = {
    0: 'Mango leaves',
    1: 'Tamarind leaves',
    2: 'Yellow Elder leaves',
    3: 'Yellow Elder leaves'   # ← เพิ่มตรงนี้
}

ALERT_COOLDOWN = 15
last_alert_time = 0

# ==========================================
# UI Theme
# ==========================================
ctk.set_appearance_mode("dark")
BG_COLOR = "#1B2430"
PANEL_COLOR = "#2A3644"
TAB_BG_COLOR = "#1E2733"
GREEN_BTN = "#2F855A"
ORANGE_BTN = "#D05A44"
FONT_FAMILY = "Kanit"

VIDEO_WIDTH, VIDEO_HEIGHT = 520, 360
CORNER_RADIUS = 20

root = ctk.CTk()
root.title("Fish Pond Guardian - Real-Time Leaf Detection")
root.geometry("1000x780")
root.configure(fg_color=BG_COLOR)

# Rounded Mask
global_mask = Image.new("L", (VIDEO_WIDTH, VIDEO_HEIGHT), 0)
draw = ImageDraw.Draw(global_mask)
draw.rounded_rectangle((0, 0, VIDEO_WIDTH, VIDEO_HEIGHT), CORNER_RADIUS, fill=255)
global_bg = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), BG_COLOR)

def get_rounded_image(cv2_img):
    img = Image.fromarray(cv2_img)
    img.putalpha(global_mask)
    bg = global_bg.copy()
    bg.paste(img, (0, 0), img)
    return bg

# ==========================================
# Load Model
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'leaf_model_real.pt')

ai_model = None
try:
    if os.path.exists(MODEL_PATH):
        ai_model = YOLO(MODEL_PATH)
        print("✅ Model loaded successfully")
    else:
        print(f"⚠️ Model not found: {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# ==========================================
# Header + Tab
# ==========================================
header = ctk.CTkLabel(root, text="Real-Time Automatic Leaf Detection System", 
                      font=(FONT_FAMILY, 26, "bold"), text_color="white")
header.pack(pady=(30, 15))

tabview = ctk.CTkTabview(root, width=900, height=420, fg_color=PANEL_COLOR, corner_radius=15)
tabview.pack(pady=10, padx=20)
tab_live = tabview.add("🟢 Live Camera")

live_frame = ctk.CTkFrame(tab_live, fg_color="transparent")
live_frame.pack(expand=True, fill="both", padx=20, pady=20)

live_label = tk.Label(live_frame, bg="#1B2430")
live_label.grid(row=0, column=0, padx=10)
snapshot_label = tk.Label(live_frame, bg="#1B2430")
snapshot_label.grid(row=0, column=1, padx=10)

status_label = ctk.CTkLabel(root, text="Status: Normal (Clean Water)", 
                            font=(FONT_FAMILY, 22, "bold"),
                            fg_color=GREEN_BTN, text_color="white",
                            corner_radius=20, width=500, height=60)
status_label.pack(pady=20)

# ==========================================
# ส่ง LINE Broadcast
# ==========================================
def upload_image_to_imgbb(image_path):
    try:
        with open(image_path, "rb") as file:
            response = requests.post("https://api.imgbb.com/1/upload",
                                     data={"key": IMGBB_API_KEY}, files={"image": file})
            return response.json()['data']['url'] if response.status_code == 200 else None
    except:
        return None

def send_line_broadcast(leaf_str):
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    alert_msg = f"🚨 Fish Pond Alert\n\nDetected: {leaf_str}\n\n⚠️ Risk of clogging. Please check urgently!\nTime: {now}"

    cv2.imwrite("latest_leaf.jpg", annotated_image if 'annotated_image' in globals() else np.zeros((300,300,3),np.uint8))
    img_url = upload_image_to_imgbb("latest_leaf.jpg")

    messages = [{"type": "text", "text": alert_msg}]
    if img_url:
        messages.append({"type": "image", "originalContentUrl": img_url, "previewImageUrl": img_url})

    try:
        requests.post('https://api.line.me/v2/bot/message/broadcast',
                      headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'},
                      data=json.dumps({"messages": messages}))
        print("✅ Broadcast sent")
    except Exception as e:
        print("LINE Error:", e)

# ==========================================
# Trigger Alert
# ==========================================
def trigger_alert(detected_classes_set, annotated_image):
    global last_alert_time

    print(f"🔍 Detected Classes: {detected_classes_set}")
    for c in detected_classes_set:
        print(f"   → Class {c} = {CLASS_NAMES_EN.get(c, 'Unknown')}")

    leaf_names = [CLASS_NAMES_EN.get(c, f"Unknown({c})") for c in detected_classes_set]
    leaf_str = ", ".join(leaf_names)

    # เงื่อนไขใบใหญ่ (รวม Class 3 ด้วย)
    has_large = any(c in [0, 2, 3] for c in detected_classes_set)

    cv2.imwrite("latest_leaf.jpg", annotated_image)

    # แสดงภาพ
    cv2image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    cv2image = cv2.resize(cv2image, (VIDEO_WIDTH, VIDEO_HEIGHT))
    img_rounded = get_rounded_image(cv2image)
    snapshot_label.imgtk = ImageTk.PhotoImage(image=img_rounded)
    snapshot_label.configure(image=snapshot_label.imgtk)

    if has_large:
        status_label.configure(text=f"🚨 Detected {leaf_str} !", fg_color=ORANGE_BTN)
        send_line_broadcast(leaf_str)
        print(f"🚨 ส่ง LINE แล้ว: {leaf_str}")
    else:
        status_label.configure(text=f"🟡 Detected {leaf_str} (Small Leaf)", fg_color="#D4A017")
        print(f"🟡 เจอแต่ใบเล็ก: {leaf_str}")

    last_alert_time = time.time()
    root.after(5000, lambda: status_label.configure(text="Status: Normal (Clean Water)", fg_color=GREEN_BTN))

# ==========================================
# Camera + AI
# ==========================================
current_frame = None
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

def update_frame():
    global current_frame
    ret, frame = cap.read()
    if ret:
        current_frame = frame.copy()
        display = frame.copy()
        if ai_model:
            res = ai_model.predict(frame, conf=0.60, verbose=False)
            if len(res[0].boxes) > 0:
                display = res[0].plot()
        cv2image = cv2.resize(cv2.cvtColor(display, cv2.COLOR_BGR2RGB), (VIDEO_WIDTH, VIDEO_HEIGHT))
        live_label.imgtk = ImageTk.PhotoImage(image=get_rounded_image(cv2image))
        live_label.configure(image=live_label.imgtk)
    live_label.after(15, update_frame)

def process_ai():
    global current_frame, last_alert_time
    if ai_model and current_frame is not None and (time.time() - last_alert_time) > ALERT_COOLDOWN:
        results = ai_model.predict(current_frame, conf=0.60, verbose=False)
        if len(results[0].boxes) > 0:
            annotated = results[0].plot()
            detected = {int(box.cls[0]) for box in results[0].boxes}
            trigger_alert(detected, annotated)
    root.after(500, process_ai)

update_frame()
process_ai()
root.mainloop()
cap.release()