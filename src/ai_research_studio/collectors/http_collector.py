from typing import Any

import requests


def fetch_json(url: str, timeout: int = 10) -> dict[str, Any]:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()