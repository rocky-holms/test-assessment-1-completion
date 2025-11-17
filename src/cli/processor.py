"""CSV processing and aggregation logic for export data."""

import csv
from collections import defaultdict
from typing import Iterator


def process_csv_stream(csv_lines: Iterator[str]) -> dict[str, dict[str, int]]:
    """
    Process a CSV stream and count events by patient and event type.

    Uses streaming to minimize memory usage - processes line by line
    without loading the entire file into memory.

    Args:
        csv_lines: Iterator yielding CSV lines (with headers)

    Returns:
        Nested dict: {patient_id: {event_type: count}}
    """
    # Use defaultdict for automatic initialization
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    # Parse CSV using built-in csv module
    reader = csv.DictReader(csv_lines)

    for row in reader:
        patient_id = row["patient_id"]
        event_type = row["event_type"]

        # Increment count for this patient/event_type combination
        counts[patient_id][event_type] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    return {
        patient_id: dict(event_counts) for patient_id, event_counts in counts.items()
    }


def aggregate_counts(
    count_list: list[dict[str, dict[str, int]]],
) -> dict[str, dict[str, int]]:
    """
    Aggregate counts from multiple downloads.

    Args:
        count_list: List of count dictionaries from individual downloads

    Returns:
        Aggregated counts: {patient_id: {event_type: total_count}}
    """
    aggregated: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for counts in count_list:
        for patient_id, event_counts in counts.items():
            for event_type, count in event_counts.items():
                aggregated[patient_id][event_type] += count

    # Convert to regular dicts
    return {
        patient_id: dict(event_counts)
        for patient_id, event_counts in aggregated.items()
    }


def compute_totals(patient_counts: dict[str, dict[str, int]]) -> dict[str, int]:
    """
    Compute total counts across all patients for each event type.

    Args:
        patient_counts: {patient_id: {event_type: count}}

    Returns:
        {event_type: total_count}
    """
    totals: dict[str, int] = defaultdict(int)

    for event_counts in patient_counts.values():
        for event_type, count in event_counts.items():
            totals[event_type] += count

    return dict(totals)


def format_output(patient_counts: dict[str, dict[str, int]]) -> dict:
    """
    Format the final output structure as specified in the README.

    Args:
        patient_counts: Aggregated patient counts

    Returns:
        Dictionary with 'patients' and 'totals' keys
    """
    return {
        "patients": patient_counts,
        "totals": compute_totals(patient_counts),
    }
