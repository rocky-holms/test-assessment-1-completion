"""CLI entry point for processing healthcare export data."""

import sys
import json
from cli.api_client import get_export_downloads, stream_download_csv
from cli.processor import process_csv_stream, aggregate_counts, format_output


def main():
    """
    Main CLI entry point.

    Usage:
        uv run cli <export_id>

    where export_id is one of: demo, small, large
    """
    # Parse command-line arguments
    if len(sys.argv) != 2:
        print("Usage: uv run cli <export_id>", file=sys.stderr)
        print("Example: uv run cli demo", file=sys.stderr)
        sys.exit(1)

    export_id = sys.argv[1]

    # Validate export_id
    valid_exports = ["demo", "small", "large"]
    if export_id not in valid_exports:
        print(f"Error: export_id must be one of {valid_exports}", file=sys.stderr)
        sys.exit(1)

    try:
        # Step 1: Discover downloads for this export
        download_ids = get_export_downloads(export_id)
        print(
            f"Found {len(download_ids)} downloads for export '{export_id}'",
            file=sys.stderr,
        )

        # Step 2: Process each download
        all_counts = []
        for i, download_id in enumerate(download_ids, 1):
            print(
                f"Processing download {i}/{len(download_ids)}: {download_id}",
                file=sys.stderr,
            )

            # Stream CSV data and process line by line
            csv_stream = stream_download_csv(export_id, download_id)
            counts = process_csv_stream(csv_stream)
            all_counts.append(counts)

        # Step 3: Aggregate counts across all downloads
        print("Aggregating results...", file=sys.stderr)
        aggregated = aggregate_counts(all_counts)

        # Step 4: Format and output results
        output = format_output(aggregated)

        # Print JSON to stdout (as specified in README)
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
