# google_auth_middleware.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .google_verifier import verify_google_token

providers = {
    "google": verify_google_token
}

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)
        
        auth_header = request.headers.get("Authorization", "")
        if auth_header:
            auth_provider, auth_type, auth_token = auth_header.split(":")
            if auth_provider not in providers:
                return JSONResponse(status_code=401, content={'detail': "Invalid provider"})
            if auth_type != "Bearer":
                return JSONResponse(status_code=401, content={'detail': "Invalid auth type"})   
            try:
                user_info = providers[auth_provider](auth_token)
                if user_info:
                    request.state.user = user_info
                else:
                    raise Exception("Invalid token")
            except Exception as e:
                return JSONResponse(status_code=401, content={'detail': str(e)})
        else:
            return JSONResponse(status_code=401, content={'detail': "Authorization header missing"})
        response = await call_next(request)
        return response