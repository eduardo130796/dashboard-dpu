from fastapi import APIRouter
from app.services.contracts_service import (
    get_contracts_cached,
    fetch_contracts
)
from app.utils.normalizer import normalize

router = APIRouter()


@router.get("/contracts")
def get_contracts():
    raw = get_contracts_cached()

    return [normalize(c) for c in raw]

@router.get("/contracts/refresh")
def refresh_contracts():
    data = fetch_contracts()

    if not data:
        return {
            "status": "falha ao atualizar",
            "message": "API demorou ou falhou",
        }

    return {
        "status": "atualizado",
        "total": len(data)
    }