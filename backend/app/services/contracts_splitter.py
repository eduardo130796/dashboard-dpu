# =========================
# STATUS GROUPS
# =========================

ACTIVE_STATUS = {
    "ativo_operacional",
    "ativo_com_execucao_no_ano",
    "ativo_sem_execucao",
    "vencido_com_execucao_recente",
    "vencido_com_execucao_no_ano",
}

ARCHIVED_STATUS = {
    "encerrado"
}


# =========================
# CLASSIFICAÇÃO
# =========================

def classify_contract(contract):
    status = contract.get("analysis", {}).get("status_real")

    if status in ACTIVE_STATUS:
        return "active"

    if status in ARCHIVED_STATUS:
        return "archived"

    # fallback explícito
    return "archived"


# =========================
# SPLIT PRINCIPAL
# =========================

def split_contracts(contracts):
    active = []
    archived = []

    for c in contracts:
        classification = classify_contract(c)

        if classification == "active":
            active.append(c)
        else:
            archived.append(c)

    return active, archived