from flask import Flask, request, jsonify, render_template
import sqlite3
import qrcode
import os

app = Flask(__name__)

DB_NAME = "wishes.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS wishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit")
def submit_page():
    return render_template("submit.html")

@app.route("/add", methods=["POST"])
def add_wish():
    data = request.get_json()
    wish = data.get("wish")

    if not wish:
        return jsonify({"error": "Wish cannot be empty"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO wishes (text) VALUES (?)", (wish,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Wish added successfully!"})

@app.route("/wishes")
def get_wishes():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT text FROM wishes")
    wishes = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify(wishes)

@app.route("/qrcode")
def generate_qr():
    site_url = request.host_url
    img = qrcode.make(site_url)
    qr_path = "static/qr.png"
    os.makedirs("static", exist_ok=True)
    img.save(qr_path)
    return f'<img src="/{qr_path}" alt="QR Code">'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
