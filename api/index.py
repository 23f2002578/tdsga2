import time, uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

ALLOWED_ORIGIN = "https://dash-jozfvh.example.com"
EMAIL = "23f2002578@ds.study.iitm.ac.in"

app = FastAPI()

class CORSAndTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        start = time.time()

        if request.method == "OPTIONS":
            resp = JSONResponse({})
            if origin == ALLOWED_ORIGIN:
                resp.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
                resp.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "*"
            resp.headers["X-Request-ID"] = str(uuid.uuid4())
            resp.headers["X-Process-Time"] = f"{time.time()-start:.6f}"
            return resp

        response = await call_next(request)
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["X-Request-ID"] = str(uuid.uuid4())
        response.headers["X-Process-Time"] = f"{time.time()-start:.6f}"
        return response

app.add_middleware(CORSAndTimingMiddleware)

@app.get("/stats")
def stats(values: str):
    nums = [int(x) for x in values.split(",") if x.strip() != ""]
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums)
    
    }
import jwt
from pydantic import BaseModel

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

ISS = "https://idp.exam.local"
AUD = "tds-ybj908jh.apps.exam.local"

class TokenReq(BaseModel):
    token: str

@app.post("/verify")
def verify(req: TokenReq):
    try:
        claims = jwt.decode(
            req.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=AUD,
            issuer=ISS,
            options={"require": ["exp", "iss", "aud"]},
        )
        return {
            "valid": True,
            "email": claims.get("email"),
            "sub": claims.get("sub"),
            "aud": claims.get("aud"),
        }
    except Exception:
        return JSONResponse(status_code=401, content={"valid": False})
