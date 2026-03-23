import requests
import datetime
import subprocess
import re
import cv2
import time
import os

SERVER = "http://127.0.0.1:5000/api/event"
USER_TO_MONITOR = "clide"
PHOTO_FOLDER = "Safe_folder"

os.makedirs(PHOTO_FOLDER, exist_ok=True)

# ===== SEND EVENT =====
def send_event(event_type, message):
    try:
        requests.post(SERVER, json={
            "type": event_type,
            "message": message,
            "time": str(datetime.datetime.now())
        })
        print("[SENT]", event_type)
    except:
        print("[ERROR] Cannot reach server")

# ===== CAMERA CAPTURE =====
def capture_intruder():
    try:
        cap = cv2.VideoCapture(0)
        time.sleep(1)

        if not cap.isOpened():
            print("[WARNING] Camera not available")
            return None

        ret, frame = cap.read()
        if ret:
            filename = f"{PHOTO_FOLDER}/intruder_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            print("[PHOTO SAVED]", filename)
            return filename
    except Exception as e:
        print("[ERROR] Camera failed:", e)
    finally:
        if 'cap' in locals():
            cap.release()

# ===== AUTH LOG MONITOR =====
def monitor_auth_log():
    print("[INFO] Monitoring login activity...")

    failed_pattern = re.compile(r"authentication failure.*user=" + re.escape(USER_TO_MONITOR))
    success_pattern = re.compile(r"session opened for user " + re.escape(USER_TO_MONITOR))

    process = subprocess.Popen(
        ["tail", "-F", "/var/log/auth.log"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    failed_count = 0

    for line in iter(process.stdout.readline, ''):

        # FAILED LOGIN
        if failed_pattern.search(line):
            failed_count += 1
            print("[FAILED LOGIN]")

            send_event("FAILED_LOGIN", "Failed login attempt detected")

            # capture photo after 3 fails
            if failed_count >= 3:
                photo = capture_intruder()
                send_event("INTRUDER_DETECTED", f"Intruder suspected. Photo: {photo}")

        # SUCCESS LOGIN
        elif success_pattern.search(line):
            print("[SUCCESS LOGIN]")
            failed_count = 0
            send_event("SUCCESS_LOGIN", "User logged in successfully")

# ===== MAIN =====
if __name__ == "__main__":
    monitor_auth_log()