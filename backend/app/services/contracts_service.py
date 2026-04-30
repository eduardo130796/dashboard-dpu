import requests
import json
import os

CACHE_FILE = "contracts_cache.json"

URL = "https://contratos.comprasnet.gov.br/api/contrato/ug/290002"


def save_cache(data):
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE, "r") as f:
        try:
            data = json.load(f)
            return data
        except:
            return None


def fetch_contracts():
    print("🌐 Buscando API externa...")

    response = requests.get(
        URL,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
    )

    print("Status:", response.status_code)

    response.raise_for_status()

    data = response.json()

    print("💾 Salvando cache...")
    save_cache(data)

    return data


def get_contracts_cached():
    cached = load_cache()

    if cached and isinstance(cached, list) and len(cached) > 0:
        print("⚡ Usando cache local")
        return cached

    print("📦 Cache vazio, buscando API...")
    return fetch_contracts()