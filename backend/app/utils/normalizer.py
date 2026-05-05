from datetime import datetime

def parse_valor(valor):
    if not valor:
        return 0
    try:
        return float(valor.replace('.', '').replace(',', '.'))
    except:
        return 0


def dias_restantes(data_fim):
    if not data_fim:
        return None

    try:
        fim = datetime.strptime(data_fim[:10], "%Y-%m-%d")
        hoje = datetime.now()
        return (fim - hoje).days
    except:
        return None


def criticidade(dias):
    if dias is None:
        return "low"
    if dias <= 30:
        return "urgent"
    elif dias <= 60:
        return "critical"
    elif dias <= 90:
        return "attention"
    return "low"


def normalize(contract):
    dias = dias_restantes(contract.get("vigencia_fim"))
    valor = parse_valor(contract.get("valor_global"))

    return {
        "id": contract.get("id"),
        "contract_number": contract.get("numero"),
        "object": contract.get("objeto"),
        "contractor": contract.get("fornecedor", {}).get("nome"),
        "status": (contract.get("situacao") or "active").lower(),
        "criticality": criticidade(dias),
        "risk_score": 50,
        "value": valor,
        "start_date": contract.get("vigencia_inicio"),
        "end_date": contract.get("vigencia_fim"),
        "category": contract.get("categoria", "services"),
        "unit": contract.get("contratante", {})
                        .get("orgao", {})
                        .get("unidade_gestora", {})
                        .get("nome_resumido"),
        "is_strategic": valor >= 5_000_000,
        "amendments_count": 0,
        "daysRemaining": dias,
        # 🔥 NOVOS CAMPOS
        "process_number": contract.get("processo"),
        "modality": contract.get("modalidade"),
    }