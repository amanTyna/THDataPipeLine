from flask import Flask, request, jsonify
import requests


app = Flask(__name__)

THINGSBOARD_DEVICE_TOKEN = "IAA8SKCg6vUtp36vLToN"
THINGSBOARD_API_URL = "https://demo.thingsboard.io/api/v1/"  # Update to your ThingsBoard instance URL

@app.route("/", methods=["GET"])
def get_request():
    return {"status": "OK"}

def send_to_thingsboard(data):
    url = f"{THINGSBOARD_API_URL}{THINGSBOARD_DEVICE_TOKEN}/telemetry"
    try:
        #print(data)
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return 500, str(e)

@app.route("/uplink", methods=["POST"])
def get_data():
    payload = request.json
    if not payload:
        return jsonify({"error": "Missing payload"})

    decoded_payload = payload.get("decoded_payload", {})
    
    telemetry_data = {

        "temperature": decoded_payload.get("temperature"),
        "humidity": decoded_payload.get("humidity")
    }
    status_code, response_message = send_to_thingsboard(telemetry_data)
    print(f"Thingsboard API: {status_code}\nMessage: {response_message}")

    if status_code == 200:
        return jsonify({"status": "success", "message": "Data sent to ThingsBoard"}), 200
    else:
        return jsonify({"status": "error", "message": response_message}), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

