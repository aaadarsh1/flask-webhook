import json
import logging
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 🔥 Enable Logging
logging.basicConfig(level=logging.DEBUG)

SECRET_TOKEN = "your_secret_token"

# 🚦 Rate Limiting
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

@app.route("/webhook", methods=["POST"])
@limiter.limit("5 per minute")  
def webhook():
    token = request.headers.get("X-Webhook-Token")
    if token != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 403  

    try:
        data = request.get_json()
        if not data or "spreadsheetId" not in data or "sheetLink" not in data:
            return jsonify({"error": "Invalid payload"}), 400

        # 📝 Log details to Render logs
        app.logger.info(f"🔗 Sheet Link: {data['sheetLink']}")
        app.logger.info(f"📝 A1 New Value: {data['newValue']}")

        # 🚀 Run Your Custom Logic
        run_custom_script(data)

        return jsonify({"status": "Success"}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400  

def run_custom_script(data):
    """Function to handle the data from Google Sheets."""
    app.logger.info(f"🚀 Processing value: {data['newValue']}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Keep debug=True for logs
