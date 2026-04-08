from flask import Flask, request, jsonify
import hmac
import hashlib
import sqlite3
import os
import json

app = Flask(__name__)

# ============================
# Paths
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "finsight.db")

RAZORPAY_WEBHOOK_SECRET = "finsight_webhook_secret_2026"


# ============================
# DB helper
# ============================
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def add_virtual_cash(user_id, real_amount, virtual_amount):
    con = get_conn()
    cur = con.cursor()

    cur.execute("""
        UPDATE wallets
        SET balance_inr = balance_inr + ?
        WHERE user_id = ?
    """, (float(virtual_amount), user_id))

    cur.execute("""
        INSERT INTO wallet_topups (user_id, real_amount, virtual_amount, status)
        VALUES (?, ?, ?, 'SUCCESS')
    """, (user_id, float(real_amount), float(virtual_amount)))

    con.commit()
    con.close()


# ============================
# Signature verification
# ============================
def verify_signature(payload_body, received_signature):
    expected_signature = hmac.new(
        RAZORPAY_WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, received_signature)


# ============================
# Webhook endpoint
# ============================
@app.route("/razorpay-webhook", methods=["POST"])
def razorpay_webhook():

    payload_body = request.data
    received_signature = request.headers.get("X-Razorpay-Signature")

    if not verify_signature(payload_body, received_signature):
        return jsonify({"status": "invalid signature"}), 400

    data = json.loads(payload_body)
    event = data.get("event")

    if event == "payment.captured":

        payment = data["payload"]["payment"]["entity"]
        amount = payment["amount"] / 100
        notes = payment.get("notes", {})

        if not notes.get("user_id") or not notes.get("virtual_amount"):
            print("⚠ Missing metadata, skipping credit")
            return jsonify({"status": "missing metadata"}), 200

        user_id = int(notes["user_id"])
        virtual_amount = float(notes["virtual_amount"])

        add_virtual_cash(user_id, amount, virtual_amount)

        print(f"✅ Wallet credited for user {user_id}")

    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)

def is_payment_processed(payment_id):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT 1 FROM wallet_topups WHERE status=?", (payment_id,))
    exists = cur.fetchone() is not None
    con.close()
    return exists