import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # Let Arduino reset

while True:
    # Send message to Arduino
    ser.write(b"Hello\n")
    print("[Pi] Sent: Hello")

    # Block until a response is received
    response = ""
    while response == "":
        response = ser.readline().decode('utf-8').strip()

    print(f"[Arduino] {response}")

    time.sleep(2)
