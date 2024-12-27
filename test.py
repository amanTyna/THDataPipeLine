from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def get_request():
    return {"status": "OK"}

@app.route("/uplink", methods=["POST"])
def log_payload():
    payload = request.json
    if not payload:
        return {"error": "Missing payload"}, 400

    # Print the received payload to the console
    print("Received Payload:")
    print(payload)

    # Respond with acknowledgment
    return {"status": "success", "message": "Payload received"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

