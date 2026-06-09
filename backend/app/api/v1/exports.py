from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def export_status() -> dict[str, str]:
    return {"status": "not_implemented"}

