from fastapi import FastAPI
from proxy import Proxy
from body_models import Request

app = FastAPI()
proxy = Proxy()

@app.get("/")
async def alive():
    return {"message": "Running..."}

@app.post("/proxy")
async def proxy(request: Request):
    pages = await proxy.make_request(request.endpoint, request.method, request.pagination, **request.payload)
    request_object = {
        "endpoint": request.endpoint,
        "method": request.method,
        "pagination": request.pagination,
        "payload": request.payload
    }
    ...