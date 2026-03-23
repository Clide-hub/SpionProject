from flask import Flask, request, jsonify, render_template
import sqlite3
from analytics import calculate_risk

app = Flask(__name__, template_folder="templates")

DB = "database.db"

# ===== INIT DB =====
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        message TEXT,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ===== DASHBOARD ROUTE (THIS FIXES 404) =====
@app.route("/")
def dashboard():
    print("DASHBOARD LOADED")  # debug
    return render_template("dashboard.html")

# ===== RECEIVE EVENTS =====
@app.route("/api/event", methods=["POST"])
def receive_event():
    data = request.json

    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute(
        "INSERT INTO events (type, message, time) VALUES (?, ?, ?)",
        (data["type"], data["message"], data["time"])
    )

    conn.commit()
    conn.close()

    return {"status": "ok"}

# ===== GET EVENTS + RISK =====
@app.route("/api/events")
def get_events():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("SELECT * FROM events ORDER BY id DESC LIMIT 20")
    rows = c.fetchall()

    conn.close()

    risk = calculate_risk(rows)

    return jsonify({
        "events": rows,
        "risk": risk
    })

# ===== TEST ROUTE =====
@app.route("/test")
def test():
    return "SERVER WORKING"

# ===== RUN =====
if __name__ == "__main__":
    print("Running on http://127.0.0.1:5000")
    app.run(debug=True)