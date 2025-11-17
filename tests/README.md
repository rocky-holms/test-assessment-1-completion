# Tests

Comprehensive test suite for the healthcare export data processing pipeline.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration
├── test_processor.py        # Unit tests for CSV processing
├── test_api_client.py       # Unit tests for API client
└── test_integration.py      # Integration tests with mock server
```

## Running Tests

### Install Test Dependencies

```bash
uv sync --dev
```

### Run All Unit Tests

```bash
pytest -m "not integration and not slow"
```

### Run All Tests (Including Integration)

**Note:** Integration tests require the server to be running.

```bash
# Terminal 1: Start server
uv run server

# Terminal 2: Run tests
pytest
```

### Run Specific Test Files

```bash
pytest tests/test_processor.py      # Processor tests only
pytest tests/test_api_client.py     # API client tests only
pytest tests/test_integration.py    # Integration tests only
```

### Run with Coverage

```bash
pytest --cov=src/cli --cov-report=html --cov-report=term
```

View coverage report: `open htmlcov/index.html`

## Test Categories

### Unit Tests (`test_processor.py`, `test_api_client.py`)

- ✅ Fast (< 1 second total)
- ✅ No external dependencies
- ✅ Mock all HTTP calls
- ✅ Test edge cases and error handling

**Run with:**
```bash
pytest -m unit
```

### Integration Tests (`test_integration.py`)

- 🔄 Requires server running
- 🐌 Slower (processes real data)
- ✅ Validates end-to-end pipeline
- ✅ Verifies output files

**Run with:**
```bash
pytest -m integration
```

### Slow Tests

Some integration tests process large datasets (marked with `@pytest.mark.slow`).

**Skip slow tests:**
```bash
pytest -m "not slow"
```

## Test Coverage

The test suite covers:

1. **CSV Processing Logic**
   - Single/multiple patients
   - Single/multiple event types
   - Empty data
   - Large datasets

2. **Aggregation**
   - Single/multiple downloads
   - Overlapping patients
   - Different event types per download

3. **API Client**
   - Successful requests
   - HTTP errors
   - Empty responses
   - URL construction

4. **End-to-End Pipeline**
   - Full demo export processing
   - Output validation
   - Comparison with saved files

5. **Output Validation**
   - JSON structure
   - Total calculations
   - Expected event types

## Example Test Output

```
tests/test_processor.py::TestProcessCsvStream::test_single_patient_single_event_type PASSED
tests/test_processor.py::TestProcessCsvStream::test_multiple_patients_multiple_event_types PASSED
tests/test_api_client.py::TestGetExportDownloads::test_get_downloads_success PASSED
tests/test_integration.py::TestOutputValidation::test_totals_match_patient_sums[demo] PASSED

====== 45 passed in 2.34s ======
```

## Continuous Integration

For CI pipelines, run fast tests only:

```bash
pytest -m "not integration and not slow" --cov=src/cli
```

