from flask import Flask, render_template, jsonify
import razorpay
from datetime import datetime

app = Flask(__name__)

# 🔑 Replace with your Razorpay keys
client = razorpay.Client(auth=("rzp_test_TIQgFkh3wARwFn", "dsOenb49tAr4g5tWBtbA9AKj"))


def fetch_donations():
    payments = client.payment.all()

    donations = []
    total = 0

    for payment in payments['items']:
        if payment['status'] == 'captured':

            amount = payment['amount'] / 100
            time = datetime.fromtimestamp(payment['created_at']).strftime('%d %b %Y, %I:%M %p')

            donations.append({
                "amount": amount,
                "time": time
            })

            total += amount

    # Latest first
    donations = donations[::-1]
    last = donations[0] if donations else None

    return total, donations, last


@app.route("/")
def home():
    total, donations, last = fetch_donations()
    return render_template("index.html", total=total, donations=donations, last=last)


@app.route("/get_total")
def get_total():
    total, donations, last = fetch_donations()
    return jsonify({
        "total": total,
        "donations": donations,
        "last": last
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)