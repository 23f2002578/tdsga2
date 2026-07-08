# api/config.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import yaml, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DEFAULTS = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}

def load_yaml(env="development"):
    try:
        with open(f"config.{env}.yaml") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}

def load_dotenv(path=".env"):
    d = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return d

def to_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes", "on")

def coerce(key, val):
    if key in ("port", "workers"):
        return int(val)
    if key == "debug":
        return to_bool(val)
    return str(val)

@app.get("/effective-config")
def effective_config(request: Request):
    cfg = dict(DEFAULTS)
    cfg.update(load_yaml("development"))
    dotenv = load_dotenv()
    mapping = {"APP_PORT": "port", "NUM_WORKERS": "workers", "APP_LOG_LEVEL": "log_level",
               "APP_DEBUG": "debug", "APP_API_KEY": "api_key", "APP_WORKERS": "workers"}
    for k, v in dotenv.items():
        key = mapping.get(k, k.replace("APP_", "").lower())
        cfg[key] = v
    for k, v in os.environ.items():
        if k.startswith("APP_"):
            key = mapping.get(k, k[4:].lower())
            cfg[key] = v
    sets = request.query_params.getlist("set")
    for s in sets:
        if "=" in s:
            k, v = s.split("=", 1)
            cfg[k.strip()] = v.strip()
    result = {k: coerce(k, cfg.get(k)) for k in ["port", "workers", "debug", "log_level", "api_key"]}
    result["api_key"] = "****"
    return result
