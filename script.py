from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

THINGSBOARD_DEVICE_TOKEN = "66o1EJj6uOAVnJuczXn2"
THINGSBOARD_API_URL = "https://demo.thingsboard.io/api/v1/"

@app.route("/", methods=["GET"])
def get_request():
    return {"status": "OK"}

def send_to_thingsboard(data):
    url = f"{THINGSBOARD_API_URL}{THINGSBOARD_DEVICE_TOKEN}/telemetry"
    try:
        print(f"Sending data to ThingsBoard: {data}")
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to ThingsBoard: {e}")
        return 500, str(e)

@app.route("/uplink", methods=["POST"])
def get_data():
    payload = request.json
    print(f"Received Payload: {payload}")  # Debugging received payload

    if not payload:
        return jsonify({"error": "Missing payload"}), 400

    try:
        # Navigate through nested JSON to extract temperature and humidity
        uplink_message = payload.get("uplink_message", {})
        decoded_payload = uplink_message.get("decoded_payload", {})

        temperature = decoded_payload.get("temperature")
        humidity = decoded_payload.get("humidity")

        # Check if telemetry data is valid
        if temperature is None or humidity is None:
            return jsonify({"error": "Missing temperature or humidity", "decoded_payload": decoded_payload}), 400

        # Prepare telemetry data
        telemetry_data = {
            "temperature": temperature,
            "humidity": humidity
        }

        # Send telemetry data to ThingsBoard
        status_code, response_message = send_to_thingsboard(telemetry_data)
        print(f"ThingsBoard API Response: {status_code} - {response_message}")

        if status_code == 200:
            return jsonify({"status": "success", "message": "Data sent to ThingsBoard"}), 200
        else:
            return jsonify({"status": "error", "message": response_message}), status_code

    except Exception as e:
        print(f"Error processing payload: {e}")
        return jsonify({"error": "Failed to process payload", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
