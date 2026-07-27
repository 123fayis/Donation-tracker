from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import razorpay
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///donations.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Razorpay client
client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))

WEBHOOK_SECRET = "mysecret123"


# 🧱 DATABASE MODEL
class Donation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    time = db.Column(db.String(100), nullable=False)


# Create DB
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


# 📊 API for frontend
@app.route("/data")
def get_data():
    donations = Donation.query.order_by(Donation.id.desc()).limit(10).all()

    total = db.session.query(db.func.sum(Donation.amount)).scalar() or 0

    last = donations[0] if donations else None

    return jsonify({
        "total": total,
        "donations": [
            {"amount": d.amount, "time": d.time} for d in donations
        ],
        "last": {"amount": last.amount, "time": last.time} if last else None
    })


# 💳 Razorpay webhook
@app.route("/webhook", methods=["POST"])
def razorpay_webhook():
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

        donation = Donation(amount=amount, time=time)
        db.session.add(donation)
        db.session.commit()

        return "OK", 200

    except Exception as e:
        print("Webhook error:", e)
        return "Invalid", 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)