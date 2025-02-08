import os
import json
import pygsheets
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# 🔒 Security Token to verify requests (must match Google Apps Script)
SECRET_TOKEN = "your_secret_token"

# 🚦 Rate Limiting: Max 5 requests per minute per IP
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per minute"])

# 🔑 Load Google Sheets Credentials from Environment Variable
service_account_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
gc = pygsheets.authorize(custom_credentials=service_account_info)

# 📊 Google Sheets link
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1g_oLFRdOzuFxj78xo4waURNWvEvnnoq_ODkRfmtj1Zc/edit?gid=0#gid=0"
spreadsheet = gc.open_by_url(SPREADSHEET_URL)
worksheet = spreadsheet.sheet1  # Get the first sheet

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

        # 📌 Step 3: Log Received Data
        app.logger.info(f"🔗 Received update from: {data['sheetLink']}")
        app.logger.info(f"📌 Cell A1 changed to: {data['newValue']}")

        # 🚀 Step 4: Run Custom Processing
        run_custom_script(data)

        return jsonify({"status": "Success"}), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400  # Handle malformed requests

def run_custom_script(data):
    """Function to handle the data from Google Sheets and update the sheet."""
    new_value = data["newValue"]

    # Log A1 edit to Render logs
    app.logger.info(f"🚀 Processing value from A1: {new_value}")

    # Read A1 value again (for verification)
    cell_value = worksheet.cell('A1').value
    app.logger.info(f"✅ Verified A1 Value: {cell_value}")

    # Write A1 value to A2
    worksheet.update_value('A2', cell_value)
    app.logger.info("✅ Successfully updated A2 with A1's value")

if __name__ == "__main__":
    # 🔒 Ensure HTTPS is used in production
    app.run(host="0.0.0.0", port=5000, debug=False)
