"""API client for interacting with the mock export server."""

import httpx
from typing import Iterator
import uuid


BASE_URL = "http://localhost:8000"


def get_export_downloads(export_id: str) -> list[uuid.UUID]:
    """
    Fetch the list of download IDs for a given export.

    Args:
        export_id: The export identifier (e.g., 'demo', 'small', 'large')

    Returns:
        List of download UUIDs for the export

    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{BASE_URL}/api/export/{export_id}"
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()

    data = response.json()
    download_ids = data["data"]["download_ids"]

    # Convert string UUIDs to UUID objects
    return [uuid.UUID(did) for did in download_ids]


def stream_download_csv(export_id: str, download_id: uuid.UUID) -> Iterator[str]:
    """
    Stream CSV data for a specific download, yielding line by line.

    Args:
        export_id: The export identifier
        download_id: The download UUID

    Yields:
        Individual lines from the CSV file (including newlines)

    Raises:
        httpx.HTTPError: If the request fails
    """
    url = f"{BASE_URL}/api/export/{export_id}/{download_id}/data"

    with httpx.stream("GET", url, timeout=None) as response:
        response.raise_for_status()

        # Stream the response line by line
        for line in response.iter_lines():
            yield line + "\n"
