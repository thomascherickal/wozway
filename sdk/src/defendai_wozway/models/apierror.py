

from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class APIError(Exception):
    """Represents an error returned by the API."""

    message: str
    status_code: int = -1
    body: str = ""
    raw_response: Optional[httpx.Response] = None

    def __str__(self):
        body = ""
        if len(self.body) > 0:
            body = f"\n{self.body}"

        return f"{self.message}: Status {self.status_code}{body}"
