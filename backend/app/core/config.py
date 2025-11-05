import os
from typing import List


def get_allowed_origins() -> List[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "")
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    return origins or ["*"]


def get_port() -> int:
    try:
        return int(os.getenv("PORT", "8000"))
    except ValueError:
        return 8000


