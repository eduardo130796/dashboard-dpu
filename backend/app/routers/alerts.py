from fastapi import APIRouter
from app.services.contracts_service import get_contracts_cached
from app.utils.normalizer import normalize
from app.services.alerts_service import build_alerts

router = APIRouter()


def normalize_list(raw):
    contracts = []
    for c in raw:
        n = normalize(c)
        if n:
            contracts.append(n)
    return contracts


@router.get("/alerts")
def get_alerts():
    raw = get_contracts_cached()

    if not raw:
        return []

    contracts = normalize_list(raw)

    return build_alerts(contracts)