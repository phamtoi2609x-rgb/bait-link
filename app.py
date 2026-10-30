# language: Python, file: app.py
# pip install flask
import json, datetime, urllib.request, os
from flask import Flask, request, send_from_directory

app = Flask(__name__, static_folder="static")
LOG = "hits.jsonl"
BOTS = ("facebookexternalhit","telegrambot","curl","wget",
        "python-requests","crawler","spider","preview")

def geo(ip):
    try:
        with urllib.request.urlopen(
            f"https://ipwho.is/{ip}", timeout=4) as r:
            d = json.loads(r.read().decode())
            if not d.get("success"): return {}
            return {
                "country": d.get("country"),
                "regionName": d.get("region"),
                "city": d.get("city"),
                "isp": d.get("connection", {}).get("isp"),
                "org": d.get("connection", {}).get("org"),
                "as": d.get("connection", {}).get("asn"),
                "lat": d.get("latitude"),
                "lon": d.get("longitude"),
            }
    except Exception:
        return {}

def log(rec):
    rec["ts"] = datetime.datetime.utcnow().isoformat() + "Z"
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/hit", methods=["POST"])
def hit():
    ua = request.headers.get("User-Agent", "")
    if any(b in ua.lower() for b in BOTS):
        return ("", 204)
    xff = request.headers.get("X-Forwarded-For", "") or ""
    ip  = (xff.split(",")[0].strip() or request.remote_addr or "").strip()
    data = request.get_json(silent=True) or {}
    data["ip"] = ip
    data["ua"] = ua
    data["geo"] = geo(ip)
    log(data)
    return ("", 204)

@app.route("/track", methods=["POST"])
def track():
    data = request.get_json(silent=True) or {}
    log({"stage":"track", **data})
    return ("", 204)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
