from fastapi import FastAPI
from proxy import Proxy
from body_models import Request

app = FastAPI()

@app.get("/")
async def alive():
    return {"message": "Running..."}

@app.post("/proxy")
async def proxy(request: Request):
    request_object = {
        "endpoint": request.endpoint,
        "method": request.method,
        "pagination": request.pagination,
        "payload": request.payload
    }
    ...