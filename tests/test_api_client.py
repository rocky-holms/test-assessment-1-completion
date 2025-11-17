"""Unit tests for API client with mocked HTTP responses."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import UUID
from cli.api_client import get_export_downloads, stream_download_csv
import httpx


class TestGetExportDownloads:
    """Tests for get_export_downloads function."""

    @patch("cli.api_client.httpx.get")
    def test_get_downloads_success(self, mock_get):
        """Test successful retrieval of download IDs."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": {
                "download_ids": [
                    "f725622a-22ea-4acc-aab8-810ec8b5e2c6",
                    "591ef21e-8a64-413a-b506-37a41cb6b896",
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_export_downloads("demo")

        assert len(result) == 2
        assert all(isinstance(uid, UUID) for uid in result)
        assert result[0] == UUID("f725622a-22ea-4acc-aab8-810ec8b5e2c6")
        mock_get.assert_called_once_with(
            "http://localhost:8000/api/export/demo", timeout=30.0
        )

    @patch("cli.api_client.httpx.get")
    def test_get_downloads_empty_list(self, mock_get):
        """Test handling of export with no downloads."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": {"download_ids": []}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = get_export_downloads("empty")

        assert result == []

    @patch("cli.api_client.httpx.get")
    def test_get_downloads_http_error(self, mock_get):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404),
        )
        mock_get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            get_export_downloads("nonexistent")


class TestStreamDownloadCsv:
    """Tests for stream_download_csv function."""

    @patch("cli.api_client.httpx.stream")
    def test_stream_csv_lines(self, mock_stream):
        """Test streaming CSV data line by line."""
        csv_content = [
            "patient_id,event_time,event_type,value",
            "P001,2025-08-26T00:00:00Z,heart_rate,75",
            "P002,2025-08-26T00:00:07Z,spo2,98",
        ]

        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.iter_lines.return_value = iter(csv_content)
        mock_response.raise_for_status = Mock()
        mock_stream.return_value = mock_response

        download_id = UUID("f725622a-22ea-4acc-aab8-810ec8b5e2c6")
        result = list(stream_download_csv("demo", download_id))

        assert len(result) == 3
        assert result[0] == "patient_id,event_time,event_type,value\n"
        assert result[1] == "P001,2025-08-26T00:00:00Z,heart_rate,75\n"
        assert all(line.endswith("\n") for line in result)

    @patch("cli.api_client.httpx.stream")
    def test_stream_csv_empty(self, mock_stream):
        """Test streaming empty CSV (headers only)."""
        csv_content = ["patient_id,event_time,event_type,value"]

        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.iter_lines.return_value = iter(csv_content)
        mock_response.raise_for_status = Mock()
        mock_stream.return_value = mock_response

        download_id = UUID("f725622a-22ea-4acc-aab8-810ec8b5e2c6")
        result = list(stream_download_csv("demo", download_id))

        assert len(result) == 1
        assert result[0] == "patient_id,event_time,event_type,value\n"

    @patch("cli.api_client.httpx.stream")
    def test_stream_csv_http_error(self, mock_stream):
        """Test handling of HTTP errors during streaming."""
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found",
            request=Mock(),
            response=Mock(status_code=404),
        )
        mock_stream.return_value = mock_response

        download_id = UUID("f725622a-22ea-4acc-aab8-810ec8b5e2c6")

        with pytest.raises(httpx.HTTPStatusError):
            list(stream_download_csv("demo", download_id))

    @patch("cli.api_client.httpx.stream")
    def test_stream_csv_url_construction(self, mock_stream):
        """Test that correct URL is constructed."""
        mock_response = MagicMock()
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = False
        mock_response.iter_lines.return_value = iter([])
        mock_response.raise_for_status = Mock()
        mock_stream.return_value = mock_response

        export_id = "demo"
        download_id = UUID("f725622a-22ea-4acc-aab8-810ec8b5e2c6")
        list(stream_download_csv(export_id, download_id))

        expected_url = (
            f"http://localhost:8000/api/export/{export_id}/{download_id}/data"
        )
        mock_stream.assert_called_once_with("GET", expected_url, timeout=None)
