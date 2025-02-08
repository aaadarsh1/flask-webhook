import json
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 🔒 Security Token to verify requests (must match Google Apps Script)
SECRET_TOKEN = "your_secret_token"

# 🚦 Rate Limiting: Max 5 requests per minute per IP
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

@app.route("/webhook", methods=["POST"])
@limiter.limit("5 per minute")  # Additional rate limiting
def webhook():
    # 🛡️ Step 1: Verify Secret Token
    token = request.headers.get("X-Webhook-Token")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403  # Reject unauthorized requests

    try:
        # 🛡️ Step 2: Validate and Extract Data
        data = request.get_json()
        if not data or "spreadsheetId" not in data or "sheetLink" not in data:
            return jsonify({"error": "Invalid payload"}), 400

        # 📌 Step 3: Print Received Data (For Debugging)
        print(f"Received update from: {data['sheetLink']}")
        print(f"Cell A1 changed to: {data['newValue']}")
        
        # 🚀 Step 4: Trigger Your Custom Script Logic
        run_custom_script(data)

        return jsonify({"status": "Success"}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400  # Handle malformed requests

def run_custom_script(data):
    """Function to handle the data from Google Sheets and execute any logic."""
    print("Running Python script logic...")
    # 🔽 Add your script logic here
    # Example: Process the new A1 value
    new_value = data["newValue"]
    print(f"Processing value: {new_value}")

if __name__ == "__main__":
    # 🔒 Ensure HTTPS is used in production
    app.run(host="0.0.0.0", port=5000, debug=False)
