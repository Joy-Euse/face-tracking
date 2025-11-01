import cv2
import time
import serial

# ----------- SERIAL CONNECTION SETUP ------------
try:
    arduino = serial.Serial('COM4', 9600, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print("✅ Connected to Arduino on COM4")
except serial.SerialException:
    print("❌ Could not connect to Arduino. Check the port or cable.")
    arduino = None

# ----------- CAMERA INITIALIZATION ------------
# Try different camera indices automatically
camera_index = -1
for i in range(5):
    cap_test = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # CAP_DSHOW helps on Windows
    if cap_test.isOpened():
        camera_index = i
        cap_test.release()
        print(f"✅ Camera found at index {i}")
        break

if camera_index == -1:
    print("❌ No available camera found. Check webcam connection.")
    exit()

cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1)

# ----------- FACE DETECTION SETUP ------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

prev_cx, prev_cy = None, None
prev_time = time.time()

print("🎥 Starting Face Tracker... Press 'Q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not captured. Reconnecting camera...")
        cap.release()
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))

    current_time = time.time()
    time_diff = current_time - prev_time if prev_time else 1.0

    direction = ""
    speed = 0.0

    for (x, y, w, h) in faces:
        cx, cy = x + w // 2, y + h // 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        if prev_cx is not None:
            dx = cx - prev_cx
            if abs(dx) > 15:
                direction = "Left" if dx > 0 else "Right"
                distance = abs(dx)
                speed = distance / time_diff if time_diff > 0 else 0

                print(f"Direction: {direction}, Speed: {speed:.2f}px/s")

                if arduino:
                    if direction == "Left":
                        arduino.write(b'L')
                    elif direction == "Right":
                        arduino.write(b'R')

        prev_cx, prev_cy = cx, cy
        prev_time = current_time
        break  # Only track first detected face

    cv2.putText(frame, f"Direction: {direction}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow('🎯 Auto Face Tracker', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if arduino:
    arduino.close()
cv2.destroyAllWindows()
print("✅ Program ended. All connections closed.")
