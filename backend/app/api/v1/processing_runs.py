from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_processing_runs() -> dict[str, list[dict]]:
    return {"items": []}

