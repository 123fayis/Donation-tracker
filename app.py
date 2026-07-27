from flask import Flask, render_template, request, jsonify
import razorpay
import os
import json
from datetime import datetime

app = Flask(__name__)

# Razorpay client
client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))

WEBHOOK_SECRET = "mysecret123"

# In-memory data (use DB later)
donations = []
total = 0
last_donation = None


@app.route("/")
def index():
    return render_template("index.html")


# API for frontend live updates
@app.route("/data")
def get_data():
    return jsonify({
        "total": total,
        "donations": donations[-10:],
        "last": last_donation
    })


# Razorpay webhook
@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
    global total, last_donation

    body = request.data
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(
            body, signature, WEBHOOK_SECRET
        )

        data = json.loads(body)

        payment = data["payload"]["payment"]["entity"]

        amount = payment["amount"] / 100
        time = datetime.now().strftime("%d %b %Y, %I:%M %p")

        donation = {
            "amount": amount,
            "time": time
        }

        donations.append(donation)
        total += amount
        last_donation = donation

        return "OK", 200

    except Exception as e:
        print("Webhook error:", e)
        return "Invalid", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)