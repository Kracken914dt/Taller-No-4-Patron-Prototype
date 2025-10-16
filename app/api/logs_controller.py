from fastapi import APIRouter, Query, HTTPException
from app.domain.services.log_service import LogService

router = APIRouter()
log_service = LogService()

@router.get("/logs/recent")
def get_recent_logs(limit: int = Query(100, ge=1, le=500)):
    """
    Obtiene los logs más recientes (para dashboard).
    """
    try:
        logs = log_service.get_recent_logs(limit)
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading recent logs")