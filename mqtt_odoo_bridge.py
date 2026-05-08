import paho.mqtt.client as mqtt
import xmlrpc.client
import json

# ==========================================
# ODOO CONFIGURATION
# ==========================================
ODOO_URL = "http://localhost:8069"
ODOO_DB = "mediot"            # CHANGE THIS to your exact Odoo database name
ODOO_USER = "admin"           # CHANGE THIS to your Odoo email/username
ODOO_PASSWORD = "admin"       # CHANGE THIS to your Odoo password

# ID of the patient you want to assign these readings to
# You can find the patient ID in the Odoo URL when viewing a patient
TARGET_PATIENT_ID = 1

# ==========================================
# MQTT CONFIGURATION
# ==========================================
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "fara/mediot/sensors"

print("Connecting to Odoo...")
try:
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if uid:
        print(f"Successfully connected to Odoo! User ID: {uid}")
    else:
        print("Failed to authenticate with Odoo. Check your DB name, username, and password.")
        exit()
    odoo_models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
except Exception as e:
    print(f"Odoo connection error: {e}")
    exit()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Successfully connected to Mosquitto MQTT broker on {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker with return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"\n--- Received MQTT Data ---")
    print(payload)
    
    try:
        data = json.loads(payload)
        
        # Prevent spamming Odoo if sensor is completely unattached (0 temp, 0 bpm)
        if data.get('temperature', 0) == 0 and data.get('bpm', 0) == 0 and data.get('leads_off', True):
            print("Sensors not attached properly, skipping database insertion.")
            return

        # Prepare the payload for med.vital.reading
        reading_vals = {
            'patient_id': TARGET_PATIENT_ID,
            'temp_c': data.get('temperature', 0),
            'ecg_bpm': data.get('bpm', 0),
            # SpO2 isn't in your current JSON, but if you add it later, map it here:
            # 'spo2': data.get('spo2', 0),
            'raw_payload': payload
        }

        # Insert into Odoo via XML-RPC
        record_id = odoo_models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'med.vital.reading', 'create',
            [reading_vals]
        )
        print(f"✅ Data successfully inserted into Odoo! (Vital Reading ID: {record_id})")

    except Exception as e:
        print(f"❌ Error inserting data to Odoo: {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    print(f"Attempting to connect to Mosquitto at {MQTT_BROKER}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Listening for ESP32 data forever. Press Ctrl+C to stop.")
    client.loop_forever()
except Exception as e:
    print(f"Could not connect to Mosquitto: {e}")
    print("Please make sure Mosquitto is running in Windows Services!")
