# Test Suite for Funding Arbitrage Bot

This directory contains unit tests for the funding arbitrage bot project.

## Overview

The test suite provides comprehensive coverage for the utility functions in the `funding_arbitrage_bot.utils.helpers` module. These tests ensure the reliability and correctness of core functionality used throughout the application.

## Test Structure

### `test_helpers.py`
Contains unit tests for all utility functions in `helpers.py`:

- **Symbol Conversion Tests**: Test functions that convert between different exchange symbol formats
  - `get_backpack_symbol()` - Converts base symbols to Backpack format
  - `get_hyperliquid_symbol()` - Converts base symbols to Hyperliquid format  
  - `get_symbol_from_exchange_symbol()` - Extracts base symbols from exchange formats

- **Decimal Adjustment Tests**: Test precise decimal operations
  - `decimal_adjust()` - Tests various rounding modes and precisions

- **Safe Dictionary Access Tests**: Test safe nested dictionary access
  - `safe_get()` - Tests safe retrieval from nested dictionaries

- **Configuration Loading Tests**: Test YAML configuration file handling
  - `load_config()` - Tests loading valid/invalid configuration files

- **Funding Rate Calculation Tests**: Test arbitrage-specific calculations
  - `calculate_funding_diff()` - Tests funding rate difference calculations

- **Position Conversion Tests**: Test exchange position format conversion
  - `convert_exchange_positions_to_local()` - Tests position data transformation

- **Logging Configuration Tests**: Test logging setup
  - `configure_logging()` - Tests logger configuration with various options

- **Mathematical Utility Tests**: Test mathematical helper functions
  - `round_to_tick()` - Tests tick-based rounding
  - `format_number()` - Tests number formatting

## Running Tests

### Using pytest directly:
```bash
python -m pytest tests/ -v
```

### Using the test runner script:
```bash
python run_tests.py
```

### Running specific test classes:
```bash
python -m pytest tests/test_helpers.py::TestSymbolConversion -v
```

### Running specific test methods:
```bash
python -m pytest tests/test_helpers.py::TestSymbolConversion::test_get_backpack_symbol -v
```

## Test Coverage

The current test suite provides **35 test cases** covering:
- ✅ Symbol conversion functions (5 tests)
- ✅ Decimal adjustment operations (5 tests)  
- ✅ Safe dictionary access (4 tests)
- ✅ Configuration file loading (3 tests)
- ✅ Funding rate calculations (4 tests)
- ✅ Position data conversion (3 tests)
- ✅ Logging configuration (3 tests)
- ✅ Mathematical utilities (8 tests)

## Test Configuration

- **pytest.ini**: Contains pytest configuration settings
- **Test discovery**: Automatically finds test files matching `test_*.py`
- **Verbose output**: Tests run with detailed output by default
- **Error handling**: Short traceback format for cleaner output

## Adding New Tests

When adding new functionality to the project:

1. Create test files following the naming convention `test_<module_name>.py`
2. Organize tests into classes using the pattern `Test<FeatureName>`
3. Name test methods with descriptive names starting with `test_`
4. Include docstrings explaining what each test validates
5. Test both normal operation and edge cases
6. Ensure all tests pass before committing changes

## Dependencies

The test suite requires:
- `pytest>=8.0.0` - Testing framework
- All project dependencies from `requirements.txt`

## Future Improvements

Potential areas for expanding test coverage:
- Integration tests for exchange API modules
- Tests for the arbitrage engine logic
- Mock tests for external API calls
- Performance tests for critical functions
- End-to-end tests for complete trading workflows