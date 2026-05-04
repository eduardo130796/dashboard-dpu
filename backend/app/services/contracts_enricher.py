from datetime import datetime, timedelta


# =========================
# HELPERS
# =========================

def parse_money(value):
    if not value:
        return 0.0

    try:
        return float(str(value).replace(".", "").replace(",", "."))
    except:
        return 0.0


def safe_parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d")
    except:
        return None


def get_empenhos(contract):
    empenhos = contract.get("empenhos")

    if not empenhos:
        return []

    if isinstance(empenhos, dict):
        return empenhos.get("lista", [])

    if isinstance(empenhos, list):
        return empenhos

    return []


# =========================
# EXECUÇÃO
# =========================

def analyze_execution(contract):
    empenhos = get_empenhos(contract)

    now = datetime.utcnow()
    ano_atual = now.year
    limite_recente = now - timedelta(days=90)

    has_ever = False
    has_year = False
    has_recent = False

    for e in empenhos:
        pago = parse_money(e.get("pago"))

        if pago <= 0:
            continue

        has_ever = True

        data_str = (
            e.get("data_emissao")
            or e.get("data")
            or e.get("data_pagamento")
        )

        data = safe_parse_date(data_str)

        if not data:
            continue

        if data.year == ano_atual:
            has_year = True

        if data >= limite_recente:
            has_recent = True

    return {
        "has_execution_ever": has_ever,
        "has_execution_year": has_year,
        "has_execution_recent": has_recent
    }


# =========================
# STATUS REAL
# =========================

def get_status_real(contract, execution):
    end_date = contract.get("end_date") or contract.get("vigencia_fim")

    fim = safe_parse_date(end_date)
    now = datetime.utcnow()

    if not fim:
        return "indefinido"

    # 🟢 CONTRATO VIGENTE
    if fim >= now:
        if execution["has_execution_recent"]:
            return "ativo_operacional"

        if execution["has_execution_year"]:
            return "ativo_com_execucao_no_ano"

        return "ativo_sem_execucao"

    # 🔴 CONTRATO VENCIDO
    if execution["has_execution_recent"]:
        return "vencido_com_execucao_recente"

    if execution["has_execution_year"]:
        return "vencido_com_execucao_no_ano"

    return "encerrado"


# =========================
# VALIDAÇÕES
# =========================

def has_responsavel(contract):
    return bool(contract.get("responsaveis"))


def has_garantia(contract):
    return bool(contract.get("garantias"))


# =========================
# ENRICH PRINCIPAL
# =========================

def enrich(contract):
    execution = analyze_execution(contract)

    responsavel = has_responsavel(contract)
    garantia = has_garantia(contract)

    flags = []

    # 👤 RESPONSÁVEL
    if not responsavel:
        flags.append("sem_responsavel")

    # 🔒 GARANTIA
    if not garantia:
        flags.append("sem_garantia")

    # 💰 EXECUÇÃO
    if not execution["has_execution_ever"]:
        flags.append("nunca_executado")

    else:
        if not execution["has_execution_recent"]:
            flags.append("sem_execucao_recente")

        if not execution["has_execution_year"]:
            flags.append("sem_execucao_no_ano")

    status_real = get_status_real(contract, execution)

    return {
        "analysis": {
            **execution,
            "has_responsavel": responsavel,
            "has_garantia": garantia,
            "status_real": status_real,
            "flags": flags
        }
    }