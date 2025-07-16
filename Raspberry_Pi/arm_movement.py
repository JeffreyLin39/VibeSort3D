import serial
import time
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device:
            return port.device
    return None

def open_serial(baudrate=9600, timeout=2):
    arduino_port = find_arduino_port()
    ser = serial.Serial(arduino_port, baudrate, timeout=timeout)
    time.sleep(2)  
    return ser

def construct_serial_message(center_x, center_y, bin_position):
    return f"{float(center_x)},{float(center_y)},{bin_position:.2f}\n"

def send_and_wait(serial_conn, message, expected_response="DONE"):
    serial_conn.write(message.encode())
    print("Sent to Arduino:", message.strip())

    while True:
        line = serial_conn.readline().decode().strip()
        if line:
            print("📥 Arduino response:", line)
        if line == expected_response:
            break
