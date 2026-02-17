import serial
import serial.tools.list_ports
import time

def find_arduino_ports():
    """Find all Arduino-like serial ports."""
    ports = serial.tools.list_ports.comports()
    arduino_ports = []
    for port in ports:
        if "Arduino" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device:
            arduino_ports.append(port.device)
    return arduino_ports

def identify_arduinos(baudrate=9600, timeout=2):
    """
    Find all Arduinos and identify them by handshake.
    Returns (gantry_ser, motor_ser) tuple.
    """
    ports = find_arduino_ports()
    
    gantry_ser = None
    motor_ser = None
    
    for port in ports:
        try:
            ser = serial.Serial(port, baudrate, timeout=timeout)
            time.sleep(2)  # Wait for Arduino to reset after serial connection
            
            # Clear any startup messages
            ser.reset_input_buffer()
            
            # Send ID query
            ser.write(b"ID\n")
            time.sleep(0.5)
            response = ser.readline().decode().strip()
            
            if response == "GANTRY":
                gantry_ser = ser
                print(f"✅ Found GANTRY on {port}")
            elif response == "MOTOR":
                motor_ser = ser
                print(f"✅ Found MOTOR on {port}")
            else:
                print(f"❓ Unknown device on {port}: '{response}'")
                ser.close()
        except Exception as e:
            print(f"❌ Error on {port}: {e}")
    
    return gantry_ser, motor_ser

def open_serial(baudrate=9600, timeout=2):
    """Legacy function - opens first Arduino found."""
    ports = find_arduino_ports()
    if ports:
        ser = serial.Serial(ports[0], baudrate, timeout=timeout)
        time.sleep(2)
        return ser
    return None

def construct_serial_message(center_x, center_y, bin_position):
    return f"{float(center_x)},{float(center_y)},{bin_position:.2f}\n"

def send_and_wait(serial_conn, message, expected_response="DONE"):
    serial_conn.write(message.encode())
    print("📤 Sent to Arduino:", message.strip())

    while True:
        line = serial_conn.readline().decode().strip()
        if line:
            print("📥 Arduino response:", line)
        if line == expected_response:
            break

# Motor control functions
def motor_on(motor_ser):
    """Turn vibrating motor ON."""
    if motor_ser:
        motor_ser.write(b"ON\n")
        print("🔔 Motor ON")

def motor_off(motor_ser):
    """Turn vibrating motor OFF."""
    if motor_ser:
        motor_ser.write(b"OFF\n")
        print("🔕 Motor OFF")
