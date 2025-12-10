from flask import Flask, render_template
import requests
import os

app = Flask(__name__)

COORDINATOR_URL = os.getenv("COORDINATOR_URL", "http://localhost:5000")

@app.route("/")
def index():
    try:
        stats = requests.get(f"{COORDINATOR_URL}/api/network/stats", timeout=5).json()
    except Exception:
        stats = None

    return render_template("index.html", stats=stats)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)