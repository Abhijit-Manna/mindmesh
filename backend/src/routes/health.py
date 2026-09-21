from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}


@router.get("/api/v1/health", status_code=200)
async def versioned_health_check():
    return {"status": "ok"}