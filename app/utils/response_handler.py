from typing import Any

def response(
    success: bool,
    status_code: int,
    message: str,
    data: Any = None,
    meta: Any = None,
):
    return {
        "success": success,
        "status_code": status_code,
        "message": message,
        "data": data,
        "meta": meta
    }
