@app.route("/uplink", methods=["POST"])
def get_data():
    payload = request.json
    print(f"Received Payload: {payload}")  # Debugging received payload

    if not payload:
        return jsonify({"error": "Missing payload"}), 400

    try:
        # Extract device_id from payload
        device_id = payload.get("data", {}).get("uplink_message", {}).get("end_device_ids", {}).get("device_id")
        print(f"Extracted device_id: {device_id}")

        if not device_id:
            return jsonify({"error": "Missing device_id in payload"}), 400

        # Extract telemetry data
        decoded_payload = payload.get("data", {}).get("uplink_message", {}).get("decoded_payload", {})
        print(f"Extracted decoded_payload: {decoded_payload}")

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
