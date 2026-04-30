from fastapi import APIRouter
from app.services.contracts_service import get_contracts_cached
from app.utils.normalizer import normalize
from app.services.dashboard_service import build_dashboard
from app.services.alerts_service import build_alerts

router = APIRouter()


def normalize_list(raw):
    contracts = []
    for c in raw:
        n = normalize(c)
        if n:
            contracts.append(n)
    return contracts


@router.get("/dashboard")
def get_dashboard():
    raw = get_contracts_cached()

    contracts = [normalize(c) for c in raw]

    dashboard = build_dashboard(contracts)
    alerts = build_alerts(contracts)

    return {
        "contracts": contracts,
        "alerts": alerts,
        "stats": dashboard["kpis"],
        "charts": dashboard["charts"],
        "urgentActions": dashboard["urgentActions"],
        "insights": dashboard["insights"]
    }