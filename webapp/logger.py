import json
import time
from datetime import datetime
import mysql.connector
from pymodbus.client import ModbusSerialClient
StatusPath = r"C:\Users\ADMIN\Desktop\IASYS\status.json"
ConfigPath = r"C:\Users\ADMIN\Desktop\IASYS\config.json"
def update_status(status: dict):
    """Write status to status.json for Streamlit to read."""
    try:
        with open(StatusPath, "w") as f:
            json.dump(status, f, indent=2)
    except Exception as e:
        print(f"Error writing status: {e}")

def main():
    # Load config
    try:
        with open(ConfigPath, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        update_status({"running": False, "error": f"Cannot read config: {e}"})
        print(f"Config error: {e}")
        return

    # Modbus connection
    modbus = None
    try:
        modbus = ModbusSerialClient(
            port=cfg["modbus"]["port"],
            baudrate=cfg["modbus"]["baudrate"],
            stopbits=cfg["modbus"]["stopbits"],
            parity=cfg["modbus"]["parity"],
            bytesize=cfg["modbus"]["bytesize"],
            timeout=1
        )
        
        if not modbus.connect():
            update_status({"running": False, "error": "Modbus connection failed"})
            print("Modbus connection failed")
            return
        else:
            print("Modbus connection successful")
            
    except Exception as e:
        update_status({"running": False, "error": f"Modbus error: {e}"})
        print(f"Modbus error: {e}")
        return

    # SQL connection
    db = None
    cursor = None
    try:
        db = mysql.connector.connect(
            host=cfg["mysql"]["host"],
            user=cfg["mysql"]["user"],
            password=cfg["mysql"]["password"],
            database=cfg["mysql"]["database"]
        )
        cursor = db.cursor()
        print("MySQL connection successful")
        
    except Exception as e:
        update_status({"running": False, "error": f"MySQL error: {e}"})
        print(f"MySQL error: {e}")
        if modbus:
            modbus.close()
        return

    update_status({"running": True, "message": "Logger started"})
    print("Logger started successfully")

    try:
        while True:
            # Read holding registers starting at address 0
            try:
                rr = modbus.read_holding_registers(address=0, count=10)

                if rr.isError() or rr is None:
                    update_status({"running": True, "warning": "Modbus read error"})
                    print("Modbus read error")
                    time.sleep(1)
                    continue
                
                # Check if we got enough registers
                if len(rr.registers) < 10:
                    update_status({"running": True, "warning": f"Only got {len(rr.registers)} registers, expected 10"})
                    print(f"Only got {len(rr.registers)} registers, expected 10")
                    time.sleep(1)
                    continue

                values = rr.registers
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert into DB
                try:
                    cursor.execute(
                        "INSERT INTO vfd (Date_Time, Control_Word, Status_Word, Reference_1, Reference_2, Speed, Torque, Voltage, Current_i, Power, Error_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (ts, values[0], values[1], values[2], values[3], values[4], values[5], values[6], values[7], values[8], values[9])
                    )
                    db.commit()
                    print(f"Data logged successfully at {ts}")
                    update_status({"running": True, "message": f"Last update: {ts}"})
                    
                except Exception as e:
                    update_status({"running": True, "error": f"MySQL insert error: {e}"})
                    print(f"MySQL insert error: {e}")

            except Exception as e:
                update_status({"running": True, "error": f"Read cycle error: {e}"})
                print(f"Read cycle error: {e}")

            time.sleep(1)  # 1 second logging interval

    except KeyboardInterrupt:
        update_status({"running": False, "message": "Logger stopped by user"})
        print("Logger stopped by user")
        
    except Exception as e:
        update_status({"running": False, "error": f"Unexpected error: {e}"})
        print(f"Unexpected error: {e}")
        
    finally:
        # Clean up connections
        if modbus:
            modbus.close()
            print("Modbus connection closed")
        if cursor:
            cursor.close()
        if db:
            db.close()
            print("MySQL connection closed")

if __name__ == "__main__":
    main()