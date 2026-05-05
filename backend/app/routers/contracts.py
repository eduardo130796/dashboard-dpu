from fastapi import APIRouter
from app.services.contracts_service import (
    get_contracts_cached,
    fetch_contracts
)
from app.utils.normalizer import normalize
from app.services.contracts_enricher import enrich
from app.services.contracts_service import get_contract_detail_from_cache,reprocess_from_cache



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

@router.get("/contracts/reprocess-local")
def reprocess_local():
    data = reprocess_from_cache()

    return {
        "status": "reprocessado",
        "total": len(data)
    }



@router.get("/contracts/{contract_id}")
def get_contract_detail(contract_id: int):
    contract = get_contract_detail_from_cache(contract_id)

    if not contract:
        return {
            "status": "not_found",
            "message": "Contrato não encontrado"
        }

    return contract