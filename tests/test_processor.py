"""Unit tests for CSV processing and aggregation logic."""

from cli.processor import (
    process_csv_stream,
    aggregate_counts,
    compute_totals,
    format_output,
)


class TestProcessCsvStream:
    """Tests for process_csv_stream function."""

    def test_single_patient_single_event_type(self):
        """Test counting for one patient with one event type."""
        csv_data = """patient_id,event_time,event_type,value
P001,2025-08-26T00:00:00Z,heart_rate,75
P001,2025-08-26T00:01:00Z,heart_rate,76
P001,2025-08-26T00:02:00Z,heart_rate,74
"""
        lines = csv_data.strip().split("\n")
        result = process_csv_stream(iter(lines))

        assert result == {"P001": {"heart_rate": 3}}

    def test_multiple_patients_multiple_event_types(self):
        """Test counting for multiple patients and event types."""
        csv_data = """patient_id,event_time,event_type,value
P001,2025-08-26T00:00:00Z,heart_rate,75
P001,2025-08-26T00:01:00Z,spo2,98
P002,2025-08-26T00:02:00Z,heart_rate,80
P002,2025-08-26T00:03:00Z,heart_rate,81
P001,2025-08-26T00:04:00Z,heart_rate,76
"""
        lines = csv_data.strip().split("\n")
        result = process_csv_stream(iter(lines))

        expected = {
            "P001": {"heart_rate": 2, "spo2": 1},
            "P002": {"heart_rate": 2},
        }
        assert result == expected

    def test_empty_csv(self):
        """Test handling of CSV with only headers."""
        csv_data = "patient_id,event_time,event_type,value\n"
        lines = csv_data.strip().split("\n")
        result = process_csv_stream(iter(lines))

        assert result == {}

    def test_large_counts(self):
        """Test that counts accumulate correctly for many rows."""
        csv_data = ["patient_id,event_time,event_type,value"]
        # Generate 1000 rows for same patient/event
        for i in range(1000):
            csv_data.append(f"P001,2025-08-26T{i:06d}Z,heart_rate,75")

        result = process_csv_stream(iter(csv_data))
        assert result == {"P001": {"heart_rate": 1000}}


class TestAggregateCounts:
    """Tests for aggregate_counts function."""

    def test_aggregate_single_download(self):
        """Test aggregation with one download."""
        counts = [{"P001": {"heart_rate": 5, "spo2": 3}}]
        result = aggregate_counts(counts)

        assert result == {"P001": {"heart_rate": 5, "spo2": 3}}

    def test_aggregate_multiple_downloads_same_patient(self):
        """Test aggregating counts from multiple downloads for same patient."""
        counts = [
            {"P001": {"heart_rate": 5, "spo2": 3}},
            {"P001": {"heart_rate": 10, "spo2": 7}},
        ]
        result = aggregate_counts(counts)

        assert result == {"P001": {"heart_rate": 15, "spo2": 10}}

    def test_aggregate_multiple_downloads_different_patients(self):
        """Test aggregating counts from downloads with different patients."""
        counts = [
            {"P001": {"heart_rate": 5}},
            {"P002": {"heart_rate": 10}},
            {"P001": {"spo2": 3}},
        ]
        result = aggregate_counts(counts)

        expected = {
            "P001": {"heart_rate": 5, "spo2": 3},
            "P002": {"heart_rate": 10},
        }
        assert result == expected

    def test_aggregate_empty_list(self):
        """Test aggregating empty list of counts."""
        result = aggregate_counts([])
        assert result == {}

    def test_aggregate_preserves_all_event_types(self):
        """Test that all event types are preserved across downloads."""
        counts = [
            {"P001": {"heart_rate": 5, "bp_sys": 2}},
            {"P001": {"spo2": 3, "bp_dia": 1}},
        ]
        result = aggregate_counts(counts)

        expected = {
            "P001": {
                "heart_rate": 5,
                "bp_sys": 2,
                "spo2": 3,
                "bp_dia": 1,
            }
        }
        assert result == expected


class TestComputeTotals:
    """Tests for compute_totals function."""

    def test_totals_single_patient(self):
        """Test computing totals for one patient."""
        patient_counts = {"P001": {"heart_rate": 10, "spo2": 5}}
        result = compute_totals(patient_counts)

        assert result == {"heart_rate": 10, "spo2": 5}

    def test_totals_multiple_patients(self):
        """Test computing totals across multiple patients."""
        patient_counts = {
            "P001": {"heart_rate": 10, "spo2": 5},
            "P002": {"heart_rate": 15, "spo2": 8},
            "P003": {"heart_rate": 5, "spo2": 2},
        }
        result = compute_totals(patient_counts)

        assert result == {"heart_rate": 30, "spo2": 15}

    def test_totals_with_different_event_types_per_patient(self):
        """Test totals when patients have different event types."""
        patient_counts = {
            "P001": {"heart_rate": 10, "spo2": 5},
            "P002": {"heart_rate": 15, "bp_sys": 8},
            "P003": {"spo2": 2, "bp_sys": 3},
        }
        result = compute_totals(patient_counts)

        assert result == {
            "heart_rate": 25,
            "spo2": 7,
            "bp_sys": 11,
        }

    def test_totals_empty_patients(self):
        """Test computing totals with no patients."""
        result = compute_totals({})
        assert result == {}


class TestFormatOutput:
    """Tests for format_output function."""

    def test_format_output_structure(self):
        """Test that output has correct structure with patients and totals."""
        patient_counts = {
            "P001": {"heart_rate": 10, "spo2": 5},
            "P002": {"heart_rate": 15, "spo2": 8},
        }
        result = format_output(patient_counts)

        assert "patients" in result
        assert "totals" in result
        assert result["patients"] == patient_counts
        assert result["totals"] == {"heart_rate": 25, "spo2": 13}

    def test_format_output_matches_readme_example(self):
        """Test output format matches README specification."""
        patient_counts = {"P001": {"heart_rate": 1520, "spo2": 1470}}
        result = format_output(patient_counts)

        # Check structure matches README example
        assert isinstance(result["patients"], dict)
        assert isinstance(result["totals"], dict)
        assert all(isinstance(counts, dict) for counts in result["patients"].values())

    def test_format_output_empty(self):
        """Test formatting empty patient counts."""
        result = format_output({})

        assert result == {"patients": {}, "totals": {}}


class TestEndToEndProcessing:
    """Integration tests for the full processing pipeline."""

    def test_full_pipeline_demo_like_data(self):
        """Test complete pipeline with demo-like data."""
        # Simulate two downloads
        download1 = """patient_id,event_time,event_type,value
P001,2025-08-26T00:00:00Z,bp_sys,120
P001,2025-08-26T00:00:07Z,bp_dia,80
P002,2025-08-26T00:00:14Z,bp_sys,125
"""
        download2 = """patient_id,event_time,event_type,value
P001,2025-08-26T01:00:00Z,bp_sys,118
P002,2025-08-26T01:00:07Z,bp_dia,82
P002,2025-08-26T01:00:14Z,bp_sys,122
"""

        # Process each download
        counts1 = process_csv_stream(iter(download1.strip().split("\n")))
        counts2 = process_csv_stream(iter(download2.strip().split("\n")))

        # Aggregate
        aggregated = aggregate_counts([counts1, counts2])

        # Format output
        result = format_output(aggregated)

        expected = {
            "patients": {
                "P001": {"bp_sys": 2, "bp_dia": 1},
                "P002": {"bp_sys": 2, "bp_dia": 1},
            },
            "totals": {
                "bp_sys": 4,
                "bp_dia": 2,
            },
        }

        assert result == expected
