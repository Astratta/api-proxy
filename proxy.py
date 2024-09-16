import json
import httpx
import backoff
from typing import Dict, Callable, Any
from httpx import Limits, Timeout

def _format_request(request: Callable):
  async def wrapper(**kwargs):
    if "data" in kwargs:
      kwargs["data"] = json.dumps(kwargs["data"])
    return await request(**kwargs)
  return wrapper

def _pagination_handler(request: Callable):
    async def wrapper(self, endpoint, method, pagination: Dict[str, Any], **kwargs):
        async def _offset_limit_based():
            pages = []
            exhaust = True
            offset = kwargs["params"][pagination["fields"][0]]
            limit = kwargs["params"][pagination["fields"][1]]

            while exhaust:
                r = await request(*args, **kwargs)
                for key in r.keys():
                    if key == "total":
                        continue

                    if len(r[key]) == 0:
                        exhaust = False
                        break
                    
                    pages.append(r[key])
                    
                offset += limit
                kwargs["params"][pagination["fields"][0]] = offset ## Offset
                #kwargs["params"][pagination["fields"][1]] ## Limit
            return pages

        if pagination["type"] == "offset_limit":
            return await _offset_limit_based()

    return wrapper

class Proxy:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=Timeout(connect=5.0, read=15.0, write=15.0, pool=15.0),
            limits=Limits(max_connections=100, max_keepalive_connections=20)
        )

    @_format_request
    @_pagination_handler
    @backoff.on_exception(
        backoff.expo, 
        (httpx.RequestError, httpx.HTTPStatusError), 
        max_tries=15,
        giveup=lambda e: e.response is not None and e.response.status_code not in {429, 500, 502, 503, 504}
    )
    async def make_request(self, endpoint: str, method: str, pagination: Dict[str, Any], **kwargs):
        try:
            r = await self.client.request(method, endpoint, **kwargs)
            r.raise_for_status()
            return await r.json()
        except httpx.HTTPStatusError as e:
            print(f"Request failed: {e}")
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")