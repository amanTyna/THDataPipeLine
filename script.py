from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Mapping device IDs to ThingsBoard device tokens
DEVICE_TOKEN_MAP = {
    "th-1": "j75qG7PStFMo6T15puDK",
    "th-2": "66o1EJj6uOAVnJuczXn2",
    "th-3": "IAA8SKCg6vUtp36vLToN",
    "th-8": "GJuDUmQJJrtt8SKta6wX",
    "th-9": "45XqCSF0DX0CwoyPe09v"
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
            "temperature": temperature,
            "humidity": humidity
        }

        # Send data to ThingsBoard
        status_code, response_message = send_to_thingsboard(device_id, telemetry_data)
        print(f"ThingsBoard API Response for device {device_id}: {status_code} - {response_message}")

        if status_code == 200:
            return jsonify({"status": "success", "message": f"Data sent to ThingsBoard for device {device_id}"}), 200
        else:
            return jsonify({"status": "error", "message": response_message}), status_code

    except Exception as e:
        print(f"Error processing payload: {e}")
        return jsonify({"error": "Failed to process payload", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
