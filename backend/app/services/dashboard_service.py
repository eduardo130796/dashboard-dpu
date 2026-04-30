from collections import Counter
from datetime import datetime
from app.services.alerts_service import build_alerts


def build_dashboard(contracts):
    total = len(contracts)

    exp30 = sum(1 for c in contracts if c["daysRemaining"] is not None and c["daysRemaining"] <= 30)
    exp60 = sum(1 for c in contracts if c["daysRemaining"] is not None and c["daysRemaining"] <= 60)
    exp90 = sum(1 for c in contracts if c["daysRemaining"] is not None and c["daysRemaining"] <= 90)

    critical = sum(1 for c in contracts if c["criticality"] in ["critico", "urgente"])

    # Distribuição ordenada
    criticality_dist = Counter(c["criticality"] for c in contracts)

    criticality_order = ["urgente", "critico", "atencao", "normal", "indefinido"]

    criticality_dist_ordered = {
        k: criticality_dist.get(k, 0)
        for k in criticality_order
    }

    # Agrupamento por mês
    monthly = {}

    for c in contracts:
        if not c.get("end_date"):
            continue

        try:
            date = datetime.strptime(c["end_date"], "%Y-%m-%d")
            key = date.strftime("%b/%Y")

            monthly[key] = monthly.get(key, 0) + 1
        except:
            continue

    monthly_list = [
        {"month": k, "count": v}
        for k, v in sorted(monthly.items())
    ]

    # Ordenar ações urgentes
    urgent_actions = sorted(
        [c for c in contracts if c["criticality"] in ["urgente", "critico"]],
        key=lambda x: x["daysRemaining"] if x["daysRemaining"] is not None else 9999
    )[:10]

    # Insights
    insights = []

    if exp30 > 0:
        insights.append(f"{exp30} contratos vencem nos próximos 30 dias")

    if critical > 0:
        insights.append(f"{critical} contratos estão em situação crítica")

    if total > 0:
        insights.append(f"Total de {total} contratos monitorados")

    return {
        "kpis": {
            "totalContracts": total,
            "expiring30Days": exp30,
            "expiring60Days": exp60,
            "expiring90Days": exp90,
            "criticalContracts": critical
        },
        "charts": {
            "monthlyExpirations": monthly_list,
            "criticalityDistribution": criticality_dist_ordered
        },
        "urgentActions": urgent_actions,
        "insights": insights
    }