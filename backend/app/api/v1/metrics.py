from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_metrics() -> dict[str, list[dict]]:
    return {"items": []}

