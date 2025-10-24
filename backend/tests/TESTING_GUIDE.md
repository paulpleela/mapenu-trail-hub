# MAPENU Backend Testing Guide

## 🧪 Test Suite Overview

This directory contains comprehensive unit tests for the MAPENU backend application.

## 📁 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_calculations.py        # Tests for utils/calculations.py
├── test_terrain_analysis.py    # Tests for utils/terrain_analysis.py
├── test_dem_processing.py      # Tests for utils/dem_processing.py
└── test_routes.py              # Tests for API endpoints
```

## 🚀 Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test only calculations
pytest tests/test_calculations.py

# Test only routes
pytest tests/test_routes.py

# Test only terrain analysis
pytest tests/test_terrain_analysis.py
```

### Run Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

View coverage report by opening `htmlcov/index.html` in a browser.

### Run Tests by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only route tests
pytest -m routes

# Run only utility tests
pytest -m utils
```

### Verbose Output

```bash
pytest -v
```

### Stop at First Failure

```bash
pytest -x
```

## 📊 Test Categories

### ✅ Unit Tests (`test_calculations.py`, `test_terrain_analysis.py`, `test_dem_processing.py`)

Test individual utility functions in isolation:
- **Haversine distance calculation**
- **Rolling hills detection and analysis**
- **Trail similarity calculation**
- **Weather exposure scoring**
- **Terrain variety analysis**
- **Surface difficulty estimation**
- **DEM tile processing**

### 🌐 Integration Tests (`test_routes.py`)

Test API endpoints with mocked database:
- **GET /** - Root health check
- **GET /trails** - List all trails
- **GET /trail/{id}/similar** - Find similar trails
- **GET /analytics/overview** - Dashboard analytics
- **GET /trail/{id}/elevation-sources** - Multi-source elevation data
- **DELETE /trail/{id}** - Delete trail

## 🎯 Test Coverage Goals

- **Utility functions**: 90%+ coverage
- **Route handlers**: 80%+ coverage
- **Edge cases**: Comprehensive handling of empty/invalid inputs
- **Error scenarios**: Proper error handling validation

## 🔧 Fixtures Available

### `mock_supabase`
Mocked Supabase client for database operations

### `sample_trail_data`
Complete trail data dictionary for testing

### `sample_elevations`
Array of elevation values for testing calculations

### `sample_coordinates`
Array of GPS coordinates for testing geospatial functions

## 📝 Writing New Tests

### Test Class Structure

```python
class TestYourFunction:
    """Tests for your_function"""

    def test_normal_case(self):
        """Should handle normal input correctly"""
        result = your_function(valid_input)
        assert result == expected_output

    def test_edge_case(self):
        """Should handle edge case gracefully"""
        result = your_function(edge_case_input)
        assert result is not None

    def test_error_handling(self):
        """Should handle errors appropriately"""
        with pytest.raises(ExpectedError):
            your_function(invalid_input)
```

### Using Fixtures

```python
def test_with_fixture(sample_trail_data):
    """Test using sample trail data"""
    result = calculate_something(sample_trail_data)
    assert result > 0
```

### Mocking External Dependencies

```python
@patch("routes.trails.supabase")
def test_with_mock(mock_supabase):
    """Test with mocked Supabase"""
    mock_supabase.table.return_value.select.return_value.execute.return_value.data = []
    # Your test code here
```

## 🐛 Debugging Tests

### Run with Print Statements

```bash
pytest -s
```

### Run Single Test

```bash
pytest tests/test_calculations.py::TestHaversine::test_same_point
```

### Use PDB Debugger

```python
def test_something():
    import pdb; pdb.set_trace()
    # Test code
```

Or run with:
```bash
pytest --pdb
```

## ✅ Test Checklist

When adding new features, ensure:
- [ ] Unit tests for new utility functions
- [ ] Route tests for new endpoints
- [ ] Edge case handling (empty inputs, None values)
- [ ] Error scenario coverage
- [ ] Mock external dependencies (Supabase, DEM, LiDAR)
- [ ] Tests pass in CI/CD pipeline

## 🎨 Best Practices

1. **One assertion per test** (when possible)
2. **Descriptive test names** that explain what's being tested
3. **Use fixtures** for common test data
4. **Mock external services** to keep tests fast and isolated
5. **Test edge cases** not just happy paths
6. **Keep tests independent** - no shared state between tests
7. **Use parametrize** for testing multiple inputs

### Example: Parametrized Test

```python
@pytest.mark.parametrize("input,expected", [
    (0, 0),
    (5, 25),
    (10, 100),
])
def test_square(input, expected):
    assert square(input) == expected
```

## 📈 Continuous Integration

Tests should be run automatically on:
- Every commit to main branch
- Every pull request
- Before deployment

## 🔍 Code Coverage

Current coverage can be viewed by running:

```bash
pytest --cov=. --cov-report=term-missing
```

Target: **85%+ overall coverage**

## 🤝 Contributing

When contributing tests:
1. Follow existing test structure
2. Add docstrings to test classes and methods
3. Use meaningful test data
4. Ensure all tests pass before committing
5. Update this guide if adding new test categories
