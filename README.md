# Healthcare Export Data Processor

A memory-efficient streaming solution for processing healthcare export data from CSV files. Built to handle millions of rows with minimal memory footprint using Python's standard library.

## Overview

This project processes healthcare data exports from a mock server API. Each export contains multiple CSV files with patient event data (heart rate, SpO2, blood pressure readings). The solution aggregates event counts by patient and event type across all files in an export.

**Key Features:**
- Streaming architecture handles 150M+ rows with <50MB memory
- Line-by-line CSV processing (no pandas/numpy)
- Comprehensive test suite (36 tests, 100% coverage on core logic)
- Clean, typed Python with full documentation

## Requirements

- **Python 3.13+** (uses modern type hints and features)
- [uv](https://github.com/astral-sh/uv) for dependency management

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/rocky-holms/test-assessment-1-completion.git
cd test-assessment-1-completion

# Install dependencies (includes dev dependencies for testing)
uv sync --dev
```

### Running the Solution

```bash
# Terminal 1: Start the mock server
uv run server

# Terminal 2: Run the CLI for an export
uv run cli demo    # or 'small' or 'large'
```

The output JSON will be printed to stdout with the following structure:

```json
{
  "patients": {
    "P001": {
      "heart_rate": 1520,
      "spo2": 1470
    }
  },
  "totals": {
    "heart_rate": 8000,
    "spo2": 6000
  }
}
```

## Available Exports

Three pre-configured exports are available:

| Export | Downloads | Total Rows | Patients | Event Types | Processing Time |
|--------|-----------|------------|----------|-------------|-----------------|
| `demo` | 2 | ~18K | 4 | bp_sys, bp_dia | < 1 second |
| `small` | 10 | ~7M | 6 | heart_rate, spo2 | ~10 seconds |
| `large` | 20 | ~153M | 20 | all 4 types | ~4 minutes |

Pre-computed results are available in `outputs/demo.json`, `outputs/small.json`, and `outputs/large.json`.

## Architecture

The solution is organized into three focused modules:

```
src/cli/
├── main.py          # CLI entry point and orchestration
├── api_client.py    # HTTP client for server API
└── processor.py     # CSV processing and aggregation
```

### Data Flow

1. **Discovery** - Query API for export's download IDs
2. **Streaming** - Stream each CSV file line-by-line via HTTP
3. **Processing** - Parse and aggregate event counts in memory
4. **Aggregation** - Combine counts across all downloads
5. **Output** - Format and print JSON to stdout

## Key Design Decisions

### Memory-Efficient Streaming

Uses `httpx.stream()` with Python's built-in `csv.DictReader()` for line-by-line processing. This keeps memory usage constant regardless of file size - critical for the large export with 153M+ rows.

**Memory complexity:** O(patients × event_types), not O(total rows)

### Sequential Processing

Downloads are processed one at a time rather than in parallel. This keeps code simple and maintainable while providing adequate performance for the dataset sizes involved.

### Standard Library Focus

Uses only Python's standard library (plus `httpx` for HTTP) - no pandas or numpy. This demonstrates fundamental data processing techniques and keeps dependencies minimal.

### Efficient Data Structures

Nested `defaultdict` provides O(1) event counting:

```python
counts[patient_id][event_type] += 1
```

Simple, efficient, and scales well for the patient/event_type cardinality in this dataset.

## Testing

Comprehensive test suite with 36 tests covering unit, integration, and validation scenarios:

```bash
# Run unit tests (fast, no server needed)
uv run pytest -m "not integration"

# Run all tests (requires server running in another terminal)
uv run pytest

# Run with coverage
uv run pytest --cov=src/cli --cov-report=html
```

**Coverage:** 100% on core processing logic (`api_client.py` and `processor.py`)

Test categories:
- **Unit tests** - CSV parsing, aggregation logic, API client (mocked)
- **Integration tests** - End-to-end pipeline validation with live server
- **Validation tests** - Output file structure and correctness

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Memory usage | < 50 MB | Constant regardless of file size |
| Processing speed | ~650K rows/sec | Sequential, single-threaded |
| Scalability | O(P × E) | P = patients, E = event types |

The streaming approach ensures memory usage stays constant even as dataset size increases.

## Project Structure

```
.
├── README.md              # This file
├── outputs/               # Pre-computed results
│   ├── demo.json
│   ├── small.json
│   └── large.json
├── src/
│   ├── cli/              # Implementation
│   │   ├── main.py
│   │   ├── api_client.py
│   │   └── processor.py
│   └── server/           # Mock server (provided)
│       └── main.py
├── tests/                # Test suite (36 tests)
│   ├── test_processor.py
│   ├── test_api_client.py
│   ├── test_integration.py
│   └── README.md
├── pyproject.toml        # Dependencies
└── pytest.ini            # Test configuration
```

## Implementation Notes

- **Type hints** - All functions fully typed for clarity
- **Error handling** - Fail-fast with informative error messages
- **Logging** - Progress to stderr, results to stdout
- **Deterministic** - Aggregation is commutative (order-independent)

## Dependencies

Minimal dependency footprint:

```toml
[dependencies]
httpx = ">=0.27.0"        # HTTP client with streaming support

[dev-dependencies]
pytest = ">=8.0.0"        # Testing framework
pytest-cov = ">=4.1.0"    # Coverage reporting
```

## Development

```bash
# Install with dev dependencies (if not already done)
uv sync --dev

# Run linter
uv run ruff check src/cli/ tests/

# Format code (if needed)
uv run black src/cli/ tests/

# Run all checks before committing
uv run pytest -m "not integration" && uv run ruff check src/cli/ tests/
```

## Requirements Satisfied

This implementation fulfills the following requirements:

- ✅ Discovers exports and downloads via API
- ✅ Processes CSV files efficiently (streaming)
- ✅ Handles large datasets (millions of rows)
- ✅ Aggregates counts across all downloads
- ✅ Outputs formatted JSON to stdout
- ✅ No pandas/numpy (stdlib only)
- ✅ Memory-efficient (O(P×E) not O(rows))
- ✅ Clean, readable, maintainable code
- ✅ Comprehensive test coverage

## License

This is a technical assessment project and is not licensed for public use.
