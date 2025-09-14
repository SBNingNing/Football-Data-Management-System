from typing import Any, Dict, Optional
from flask import jsonify

def success_response(data: Any = None, message: str = "OK", meta: Optional[Dict[str, Any]] = None, status_code: int = 200):
    payload = {
        "success": True,
        "message": message
    }
    if data is not None:
        payload["data"] = data
    if meta:
        payload["meta"] = meta
    return jsonify(payload), status_code


def error_response(code: str, message: str, http_status: int = 400, detail: Optional[Any] = None, meta: Optional[Dict[str, Any]] = None):
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    if detail is not None:
        payload["error"]["detail"] = detail
    if meta:
        payload["meta"] = meta
    return jsonify(payload), http_status

class AppError(Exception):
    def __init__(self, code: str, message: str, http_status: int = 400, detail: Any = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.http_status = http_status
        self.detail = detail

    def to_response(self):
        return error_response(self.code, self.message, self.http_status, self.detail)
