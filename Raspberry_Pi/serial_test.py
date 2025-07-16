import serial
import serial.tools.list_ports
import time

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device:
            return port.device
    return None

# Find the Arduino port
arduino_port = find_arduino_port()

if arduino_port is None:
    print("❌ Arduino not found.")
    exit(1)

print(f"✅ Found Arduino on {arduino_port}")

# Set up serial communication
arduino = serial.Serial(arduino_port, 9600, timeout=2)
time.sleep(2)  # Wait for Arduino reset

# Send message
message = "E\n"
arduino.write(message.encode())

# Wait for response
while True:
    line = arduino.readline().decode().strip()
    if line:
        print("Received from Arduino:", line)
        if line == "Done":
            break
