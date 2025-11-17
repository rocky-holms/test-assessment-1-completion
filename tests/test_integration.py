"""Integration tests that verify the full pipeline with the mock server."""

import pytest
import json
from cli.api_client import get_export_downloads, stream_download_csv
from cli.processor import process_csv_stream, aggregate_counts, format_output


@pytest.mark.integration
class TestIntegrationWithMockServer:
    """
    Integration tests that require the mock server to be running.

    To run these tests:
    1. Start the server: uv run server
    2. Run tests: pytest tests/test_integration.py -m integration

    Note: These tests are marked as 'integration' and can be skipped in CI
    by running: pytest -m "not integration"
    """

    def test_demo_export_end_to_end(self):
        """Test processing demo export from start to finish."""
        export_id = "demo"

        # Step 1: Get downloads
        download_ids = get_export_downloads(export_id)
        assert len(download_ids) > 0, "Demo export should have downloads"

        # Step 2: Process each download
        all_counts = []
        for download_id in download_ids:
            csv_stream = stream_download_csv(export_id, download_id)
            counts = process_csv_stream(csv_stream)
            all_counts.append(counts)

        # Step 3: Aggregate
        aggregated = aggregate_counts(all_counts)

        # Step 4: Format output
        result = format_output(aggregated)

        # Verify structure
        assert "patients" in result
        assert "totals" in result
        assert len(result["patients"]) > 0

        # Verify totals match patient sums
        calculated_totals = {}
        for patient_counts in result["patients"].values():
            for event_type, count in patient_counts.items():
                calculated_totals[event_type] = (
                    calculated_totals.get(event_type, 0) + count
                )

        assert result["totals"] == calculated_totals

    def test_output_matches_saved_files(self):
        """Test that current processing matches saved output files."""
        export_id = "demo"

        # Process the export
        download_ids = get_export_downloads(export_id)
        all_counts = []
        for download_id in download_ids:
            csv_stream = stream_download_csv(export_id, download_id)
            counts = process_csv_stream(csv_stream)
            all_counts.append(counts)

        aggregated = aggregate_counts(all_counts)
        result = format_output(aggregated)

        # Compare with saved file
        with open("outputs/demo.json") as f:
            saved_result = json.load(f)

        assert result == saved_result, "Current output should match saved output"

    @pytest.mark.slow
    def test_small_export_processing(self):
        """Test processing small export (may take several seconds)."""
        export_id = "small"

        download_ids = get_export_downloads(export_id)
        assert len(download_ids) >= 10, "Small export should have 10 downloads"

        all_counts = []
        for download_id in download_ids:
            csv_stream = stream_download_csv(export_id, download_id)
            counts = process_csv_stream(csv_stream)
            all_counts.append(counts)

        aggregated = aggregate_counts(all_counts)
        result = format_output(aggregated)

        # Verify we have patients and reasonable counts
        assert len(result["patients"]) > 0
        assert all(
            count > 0
            for patient in result["patients"].values()
            for count in patient.values()
        )

        # Verify totals are in expected range (millions of rows)
        total_events = sum(result["totals"].values())
        assert total_events > 1_000_000, "Small export should have millions of events"


@pytest.mark.unit
class TestOutputValidation:
    """Unit tests for validating saved output files."""

    @pytest.mark.parametrize("export_id", ["demo", "small", "large"])
    def test_output_file_structure(self, export_id):
        """Test that output files have correct structure."""
        with open(f"outputs/{export_id}.json") as f:
            data = json.load(f)

        # Check required keys
        assert "patients" in data
        assert "totals" in data

        # Check types
        assert isinstance(data["patients"], dict)
        assert isinstance(data["totals"], dict)

        # Check nested structure
        for patient_id, counts in data["patients"].items():
            assert isinstance(patient_id, str)
            assert isinstance(counts, dict)
            for event_type, count in counts.items():
                assert isinstance(event_type, str)
                assert isinstance(count, int)
                assert count > 0

    @pytest.mark.parametrize("export_id", ["demo", "small", "large"])
    def test_totals_match_patient_sums(self, export_id):
        """Test that totals equal sum of patient counts."""
        with open(f"outputs/{export_id}.json") as f:
            data = json.load(f)

        # Calculate totals from patients
        calculated_totals = {}
        for patient_counts in data["patients"].values():
            for event_type, count in patient_counts.items():
                calculated_totals[event_type] = (
                    calculated_totals.get(event_type, 0) + count
                )

        assert data["totals"] == calculated_totals

    def test_demo_expected_event_types(self):
        """Test that demo export has expected event types."""
        with open("outputs/demo.json") as f:
            data = json.load(f)

        # Demo should have bp_sys and bp_dia
        assert "bp_sys" in data["totals"]
        assert "bp_dia" in data["totals"]

    def test_small_expected_event_types(self):
        """Test that small export has expected event types."""
        with open("outputs/small.json") as f:
            data = json.load(f)

        # Small should have heart_rate and spo2
        assert "heart_rate" in data["totals"]
        assert "spo2" in data["totals"]

    def test_large_expected_event_types(self):
        """Test that large export has expected event types."""
        with open("outputs/large.json") as f:
            data = json.load(f)

        # Large should have all four event types
        expected_types = {"heart_rate", "spo2", "bp_sys", "bp_dia"}
        assert set(data["totals"].keys()) == expected_types
