from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
import os

app = Flask(__name__)

# MongoDB Configuration
# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")  # Update to your MongoDB URI
MONGO_URI = "mongodb+srv://timepass10999:RQpIEflYi2Jv3sDI@cluster0.rpqrt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGO_DB = "sensor_data"
MONGO_COLLECTION = "telemetry"

# Initialize MongoDB client
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# Mapping device IDs to ThingsBoard device tokens
DEVICE_TOKEN_MAP = {
    "th-1": "j75qG7PStFMo6T15puDK",
    "th-2": "66o1EJj6uOAVnJuczXn2",
    "th-3": "IAA8SKCg6vUtp36vLToN",
    "th-4": "bemXMSuIiY6H8VZBSFkR",
    "th-5": "6CAwGF9eEaObH7datlNx",
    "th-6": "sezDXyqTxGHusK7WFaG7",
    "th-7": "kAJ8oBOPabhAlV111Byz",
    "th-8": "GJuDUmQJJrtt8SKta6wX",
    "th-9": "45XqCSF0DX0CwoyPe09v",
    "th-10": "lreLMwfZWpDFDxAfyWB0",
    "th-11": "etNlRiuzW8euRAItOsAa",
    "th-12": "FwxOGg2Ip5PXGxBwecAv",
    "th-13": "1PwBRbBQunrvXbfcTiy0",
    "th-14": "tUoZcG6yRHm2ICQssFKu",
    "th-15": "4WVSJW1bcDcYxlwRgBk0",
    "th-16": "nvUYivRxoVmLzONIZBa5",
    "th-17": "G4VtgwpDJlXzZhNM71Me",
    "th-18": "LaMZ6mDfVE4s8uqYv21z",
    "th-19": "AVLJ1S4UcyLVLouSCnLm",
    "th-20": "TD5A9yiF36OJddane3bh",
    "th-21": "grKHRmkGWbWNAopxMub6",
    "th-22": "EceAK3NALfuzyHSTCtMH",
    "th-23": "LxgxAfStStcOov3O1Jmw",
    "th-24": "oHD3tEIAXeC7wVFHjnSj",
    "th-25": "NfYKkFB9wIPukTRFF51o",
    "th-26": "XKgV3JqaVlPbQ6pCwI6e",
    "th-27": "rxsmKp9fTvpTWB5waLCz",
    "th-28": "LJmfBm8RdlLohpe7IZVs",
    "th-29": "pA2NLnYnZ5KI7LALHvTh",
    "th-30": "Gi7kiaZ3JCENp9Kve3bB",
    "th-31": "Vzw8MvNmONoZMurEqLDO",
    "th-32": "EIPuKVMhb3xNSYu1FDqN",
    "th-33": "pjOolIhh2H5by2eyn4cv",
    "th-34": "YojCBBj9BLysTdheqtmf",
    "th-35": "otgeGcPeCvXnwtA27qAT",
    "th-36": "WgJVwIaFVKqGgTm4Q70X",
    "th-37": "sJcnXTobGSrQpDqttn9h",
    "th-38": "8rrzZMFEyOsvezpg3WZ9"
}

THINGSBOARD_API_URL = "https://demo.thingsboard.io/api/v1/"  # Update to your ThingsBoard instance URL

@app.route("/", methods=["GET"])
def get_request():
    return {"status": "OK"}

def send_to_thingsboard(device_id, data):
    device_token = DEVICE_TOKEN_MAP.get(device_id)
    if not device_token:
        return 400, f"Device ID {device_id} not found in token map"

    url = f"{THINGSBOARD_API_URL}{device_token}/telemetry"
    try:
        print(f"Sending data to ThingsBoard for device {device_id}: {data}")
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to ThingsBoard for device {device_id}: {e}")
        return 500, str(e)

def store_to_mongodb(data):
    try:
        mongo_collection.insert_one(data)
        print(f"Data successfully stored in MongoDB: {data}")
        return True
    except Exception as e:
        print(f"Error storing data to MongoDB: {e}")
        return False

@app.route("/uplink", methods=["POST"])
def get_data():
    payload = request.json
    print(f"Received Payload: {payload}")  # Debugging received payload

    if not payload:
        return jsonify({"error": "Missing payload", "payload": payload}), 400

    try:
        # Extract device_id from the payload
        end_device_ids = payload.get("end_device_ids", {})
        device_id = end_device_ids.get("device_id")
        print(f"Extracted device_id: {device_id}")

        if not device_id:
            return jsonify({"error": "Missing device_id in payload"}), 400

        # Extract telemetry data
        decoded_payload = payload.get("uplink_message", {}).get("decoded_payload", {})
        print(f"Extracted decoded_payload: {decoded_payload}")

        # Check device_id numerical suffix
        try:
            device_suffix = int(device_id.split('-')[-1])  # Extract numerical suffix
        except ValueError:
            return jsonify({"error": "Invalid device_id format"}), 400

        if device_suffix > 20:
            # Use `Hum_SHT` for humidity and `TempC_SHT` for temperature
            temperature = decoded_payload.get("TempC_SHT")
            humidity = decoded_payload.get("Hum_SHT")
        else:
            # Default fields
            temperature = decoded_payload.get("temperature")
            humidity = decoded_payload.get("humidity")

        if temperature is None or humidity is None:
            return jsonify({
                "error": "Missing temperature or humidity",
                "decoded_payload": decoded_payload
            }), 400

        # Prepare telemetry data
        telemetry_data = {
            "device_id": device_id,
            "temperature": temperature,
            "humidity": humidity
        }

        # Send data to ThingsBoard
        status_code, response_message = send_to_thingsboard(device_id, telemetry_data)
        print(f"ThingsBoard API Response for device {device_id}: {status_code} - {response_message}")

        # Store data in MongoDB
        store_success = store_to_mongodb(telemetry_data)

        if status_code == 200 and store_success:
            return jsonify({"status": "success", "message": f"Data sent to ThingsBoard and stored in MongoDB for device {device_id}"}), 200
        elif status_code != 200:
            return jsonify({"status": "error", "message": f"ThingsBoard Error: {response_message}"}), status_code
        elif not store_success:
            return jsonify({"status": "error", "message": "Failed to store data in MongoDB"}), 500

    except Exception as e:
        print(f"Error processing payload: {e}")
        return jsonify({"error": "Failed to process payload", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
