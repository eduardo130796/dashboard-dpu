import requests
import json
import os
from datetime import datetime

from app.services.contracts_enricher import enrich
from app.services.contracts_splitter import split_contracts
from app.utils.normalizer import normalize


CACHE_FILE = "contracts_cache.json"
ACTIVE_FILE = "contracts_active.json"
ARCHIVED_FILE = "contracts_archived.json"

URL = "https://contratos.comprasnet.gov.br/api/contrato/ug/290002"


# =========================
# CACHE (BASE COMPLETA)
# =========================

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return []

    try:
        with open(CACHE_FILE, "r") as f:
            content = f.read().strip()

            if not content:
                return []

            data = json.loads(content)
            return data.get("contracts", [])

    except Exception as e:
        print("⚠️ erro ao ler cache:", e)
        return []


def save_cache(full_data):
    payload = {
        "updated_at": datetime.utcnow().isoformat(),
        "total": len(full_data),
        "contracts": full_data
    }

    with open(CACHE_FILE, "w") as f:
        json.dump(payload, f, ensure_ascii=False)

    print(f"💾 Cache completo salvo ({len(full_data)})")


# =========================
# HELPERS
# =========================

def load_archived_ids():
    if not os.path.exists(ARCHIVED_FILE):
        return set()

    try:
        with open(ARCHIVED_FILE, "r") as f:
            content = f.read().strip()

            if not content:
                return set()

            data = json.loads(content)

            return set(c.get("id") for c in data if c.get("id"))

    except Exception as e:
        print("⚠️ erro ao ler archived:", e)
        return set()


def get_archived_cached():
    if not os.path.exists(ARCHIVED_FILE):
        return []

    try:
        with open(ARCHIVED_FILE, "r") as f:
            content = f.read().strip()

            if not content:
                return []

            return json.loads(content)

    except Exception as e:
        print("⚠️ erro ao ler archived:", e)
        return []


def fetch_safe(url):
    if not url:
        return []

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return res.json() or []
    except:
        return []


# =========================
# ENRICH BRUTO
# =========================

def enrich_contract(contract):
    links = contract.get("links", {})

    return {
        **contract,
        "empenhos": fetch_safe(links.get("empenhos")),
        "faturas": fetch_safe(links.get("faturas")),
        "garantias": fetch_safe(links.get("garantias")),
        "responsaveis": fetch_safe(links.get("responsaveis")),
        "historico": fetch_safe(links.get("historico")),
        "itens": fetch_safe(links.get("itens")),
    }


# =========================
# PROCESSAMENTO FRONT
# =========================

def process_contracts(raw_data):
    processed = []

    for c in raw_data:
        n = normalize(c)

        if not n:
            continue

        analysis = enrich(c)["analysis"]

        processed.append({
            **n,
            "analysis": analysis,
            "id": n.get("id") or c.get("id")
        })

    return processed


# =========================
# FETCH PRINCIPAL
# =========================

def fetch_contracts(limit=100):
    print("🌐 Buscando API...")

    try:
        response = requests.get(URL, timeout=60)
        response.raise_for_status()
        data = response.json()
    except:
        print("⚠️ falha API, usando cache")
        return get_contracts_cached()

    # -------------------------
    # CARREGAR BASE EXISTENTE
    # -------------------------
    full_cache = load_cache()
    cache_map = {c["id"]: c for c in full_cache if c.get("id")}

    archived_ids = load_archived_ids()

    enriched_batch = []

    # -------------------------
    # ENRICH (SEMPRE PARA CACHE)
    # -------------------------
    for i, c in enumerate(data[:limit]):
        cid = c.get("id")

        print(f"🔄 {i+1}/{limit} contrato {cid}")

        # -------------------------
        # 🔒 CONTRATO ARQUIVADO
        # -------------------------
        if cid in archived_ids:
            print(f"⏭️ ignorando arquivado: {cid}")

            # mantém no cache se já existir
            if cid not in cache_map:
                cache_map[cid] = c  # fallback mínimo

            continue

        # -------------------------
        # 🟢 CONTRATO ATIVO
        # -------------------------

        cached = cache_map.get(cid)

        # 🔒 ARQUIVADOS → NÃO ATUALIZA
        if cid in archived_ids:
            if not cached:
                cache_map[cid] = c
            continue

        # 🟢 ATIVOS → SEMPRE GARANTIR ENRIQUECIMENTO COMPLETO
        needs_update = False

        if not cached:
            needs_update = True

        # 🔥 NOVO CAMPO (ex: itens)
        elif "itens" not in cached:
            needs_update = True

        # 🔄 (opcional) se quiser atualizar sempre:
        # needs_update = True

        if needs_update:
            enriched = enrich_contract(c)
            cache_map[cid] = enriched
        else:
            enriched = cached

        enriched_batch.append(enriched)

    # -------------------------
    # SALVAR CACHE COMPLETO
    # -------------------------
    full_cache_updated = list(cache_map.values())
    save_cache(full_cache_updated)

    # -------------------------
    # PROCESSAR APENAS ATIVOS
    # -------------------------
    processed = process_contracts(enriched_batch)

    active, new_archived = split_contracts(processed)

    # -------------------------
    # MERGE ARCHIVED
    # -------------------------
    existing_archived = get_archived_cached()

    archived_map = {c["id"]: c for c in existing_archived}

    for c in new_archived:
        archived_map[c["id"]] = c

    archived = list(archived_map.values())

    # -------------------------
    # SALVAR FILES
    # -------------------------
    with open(ACTIVE_FILE, "w") as f:
        json.dump(active, f, ensure_ascii=False)

    with open(ARCHIVED_FILE, "w") as f:
        json.dump(archived, f, ensure_ascii=False)

    print(f"✅ Ativos: {len(active)} | Arquivados: {len(archived)}")

    return active


# =========================
# CACHE FIRST (FRONT)
# =========================

def get_contracts_cached():
    if os.path.exists(ACTIVE_FILE):
        with open(ACTIVE_FILE, "r") as f:
            print("⚡ usando active")
            return json.load(f)

    return fetch_contracts()

def reprocess_from_cache():
    print("♻️ Reprocessando cache local...")

    raw = load_cache()  # 🔥 usa cache existente

    if not raw:
        print("❌ Sem cache para reprocessar")
        return []

    processed = process_contracts(raw)

    active, archived = split_contracts(processed)

    # 🔥 sobrescreve os arquivos corretamente
    with open(ACTIVE_FILE, "w") as f:
        json.dump(active, f)

    with open(ARCHIVED_FILE, "w") as f:
        json.dump(archived, f)

    print(f"✅ Reprocessado | Ativos: {len(active)} | Arquivados: {len(archived)}")

    return active

def get_contract_detail_from_cache(contract_id: int):
    raw = load_cache()  # 🔥 cache completo

    if not raw:
        return None

    for c in raw:
        if str(c.get("id")) == str(contract_id):
            return c

    return None