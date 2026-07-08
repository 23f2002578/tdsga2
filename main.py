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
