from fastapi import APIRouter
from app.services.contracts_service import (
    get_contracts_cached,
    fetch_contracts
)
from app.utils.normalizer import normalize
from app.services.contracts_enricher import enrich



router = APIRouter()


@router.get("/contracts")
def get_contracts():
    return get_contracts_cached()


@router.get("/contracts/refresh")
def refresh_contracts():
    data = fetch_contracts()

    return {
        "status": "atualizado",
        "total": len(data)
    }