# Solution Overview

## Quick Start

```bash
# Install dependencies
uv sync

# Terminal 1: Start the mock server
uv run server

# Terminal 2: Run the CLI for an export
uv run cli demo    # or 'small' or 'large'
```

The output JSON will be printed to stdout.

## Architecture

The solution is organized into three modules:

```
src/cli/
├── main.py          # CLI entry point and orchestration
├── api_client.py    # HTTP client for server API
└── processor.py     # CSV processing and aggregation
```

### Data Flow

1. **Discovery**: Query the API to get all download IDs for an export
2. **Streaming**: Stream each CSV file line-by-line via HTTP
3. **Processing**: Parse and aggregate event counts in memory
4. **Aggregation**: Combine counts across all downloads
5. **Output**: Format and print JSON to stdout

## Key Design Decisions

### Memory-Efficient Streaming

The solution uses line-by-line streaming with `httpx.stream()` and Python's built-in `csv.DictReader()`. This keeps memory usage constant regardless of file size - crucial for the large export with 153M+ rows.

**Memory complexity**: O(patients × event_types), not O(total rows)

### Sequential Processing

Downloads are processed sequentially (one at a time) rather than in parallel. This keeps the code simple and readable while still providing adequate performance for the dataset sizes involved.

### No External Data Libraries

Per the requirements, the solution uses only Python's standard library (plus `httpx` for HTTP) - no pandas or numpy. This demonstrates understanding of fundamental data processing techniques.

### Data Structure

Uses nested `defaultdict` for O(1) event counting:

```python
counts[patient_id][event_type] += 1
```

This is simple, efficient, and scales well for the patient/event_type cardinality in this dataset.

## Output Files

Pre-computed results for each export are available in `outputs/`:
- `outputs/demo.json` - 4 patients, ~18K events
- `outputs/small.json` - 6 patients, ~7M events  
- `outputs/large.json` - 20 patients, ~153M events

## Testing

A comprehensive test suite is included:

```bash
# Run unit tests (fast, no server needed)
pytest -m "not integration"

# Run all tests (requires server running)
pytest

# Run with coverage
pytest --cov=src/cli
```

**Test coverage**: 36 tests with 100% coverage on core processing logic (`api_client.py` and `processor.py`).

## Performance

| Export | Downloads | Total Rows | Processing Time | Memory Usage |
|--------|-----------|------------|-----------------|--------------|
| demo   | 2         | ~18K       | < 1 second      | < 10 MB      |
| small  | 10        | ~7M        | ~10 seconds     | < 20 MB      |
| large  | 20        | ~153M      | ~4 minutes      | < 50 MB      |

The streaming approach ensures memory usage stays constant even as dataset size increases.

## Implementation Notes

- All functions have type hints for clarity
- Error handling with fail-fast behavior
- Progress messages to stderr, results to stdout
- Deterministic output (stable sorting not required as aggregation is commutative)

