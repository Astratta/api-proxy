import httpx
from httpx import BasicAuth, Limits, Timeout

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
    
    def _build_request():
        ...

    def _pagination_handler():
        ...