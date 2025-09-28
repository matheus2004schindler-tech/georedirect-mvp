import os
from flask import Flask, redirect, request
import requests, json

app = Flask(__name__)

CONFIG_FILE = "clientes.json"

def load_configs():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_remote_ip():
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr

def get_country_from_ip(ip):
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=3)
        data = resp.json()
        return data.get("country")
    except Exception:
        return None

@app.route("/")
def home():
    return """
    <h2>🌍 GeoRedirect — MVP</h2>
    <p>Use <code>/go/CLIENTE</code> para redirecionar visitantes por país.</p>
    <p>Exemplo: <a href="/go/demo">/go/demo</a></p>
    """

@app.route("/go/<client_id>")
def geo_redirect(client_id):
    configs = load_configs()
    client = configs.get(client_id)
    if not client:
        return f"<h3>❌ Cliente '{client_id}' não encontrado.</h3>", 404

    ip = get_remote_ip()
    country = get_country_from_ip(ip)

    if country and country in client.get("redirects", {}):
        target = client["redirects"][country]
    else:
        target = client.get("default_url", "https://google.com")

    return redirect(target)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
