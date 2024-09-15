import httpx
import json
from typing import Dict, Callable
from httpx import Limits, Timeout

def _format_request(request):
  def wrapper(**kwargs):
    if "data" in kwargs:
      kwargs["data"] = json.dumps(kwargs["data"])
    return request(**kwargs)
  return wrapper

def _pagination_handler(request: Callable):
    def wrapper(endpoint, method, pagination, **kwargs):
        def _offset_limit_based():
            pages = []
            offset = kwargs["params"][pagination["fields"][0]]
            limit = kwargs["params"][pagination["fields"][1]]

            while True:
                exhausted = False
                r = request(endpoint, method, pagination, **kwargs)
                
                for key in r.keys():
                    if key == "total":
                        continue

                    if len(r[key]) == 0:
                        exhausted = True
                        break
                    
                    pages.append(r[key])

                if exhausted:
                    break
                    
                offset += limit
                kwargs["params"][pagination["fields"][0]] = offset ## Offset
                #kwargs["params"][pagination["fields"][1]] ## Limit
            return pages

        if pagination["type"] == "offset_limit":
            return _offset_limit_based()

    return wrapper

class Proxy:
    def __init__(self):
        retries = httpx.Retry(
            total=15,
            backoff_factor=1,
            status_codes={429, 500, 502, 503, 504}
        )

        self.client = httpx.AsyncClient(
            timeout=Timeout(connect=5.0, read=15.0),
            limits=Limits(max_connections=100, max_keepalive_connections=20),
            transport=httpx.HTTPTransport(retries=retries)
        )

    @_format_request
    @_pagination_handler
    async def make_request(self, endpoint: str, method: str, pagination: Dict, **kwargs):
        try:
            r = self.client.request(method, endpoint, **kwargs)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            print(f"Request failed: {e}")
        except httpx.RequestError as e:
            print(f"An error occurred: {e}")