from fastapi import APIRouter

router = APIRouter(prefix="/verifications", tags=["verifications"])

@router.get("/ping")
def ping():
    return {"ok": True}
