from flask import Flask, request, jsonify, render_template, redirect, session
import sqlite3
import qrcode
import os
from utils import deduplicate_wishes
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "super_secret_key"
load_dotenv()
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
def qr_page():
    site_url = request.host_url + "home"
    img = qrcode.make(site_url)
    qr_path = "static/qr.png"
    os.makedirs("static", exist_ok=True)
    img.save(qr_path)
    return render_template("qr.html", qr_image=qr_path)

@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == os.getenv("ISM") and password == os.getenv("PASSWORD"):
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Login yoki parol noto‘g‘ri!"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

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

@app.route("/admin")
def admin_page():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT text FROM wishes")
    wishes = [row[0] for row in c.fetchall()]
    conn.close()

    grouped_wishes = deduplicate_wishes(wishes)

    return render_template("admin.html", wishes=grouped_wishes)

@app.route("/qrcode")
def generate_qr():
    site_url = request.host_url + "home"
    img = qrcode.make(site_url)
    qr_path = "static/qr.png"
    os.makedirs("static", exist_ok=True)
    img.save(qr_path)
    return f'<img src="/{qr_path}" alt="QR Code">'

@app.route("/clear_wishes", methods=["POST"])
def clear_wishes():
    if not session.get("admin"):
        return redirect("/login")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM wishes")
    conn.commit()
    conn.close()

    return ("", 204)

@app.route("/secret")
def secret():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

