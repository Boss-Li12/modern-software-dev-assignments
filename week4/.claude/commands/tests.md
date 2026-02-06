# Test Runner with Coverage

Run the project test suite with coverage reporting and provide actionable feedback.

## Usage
```
/tests [options]
```

## Arguments
- `$ARGUMENTS` - Optional pytest arguments (e.g., `-k test_notes`, `--lf`, `-x`)

## Steps

1. **Run tests with verbose output**
   ```bash
   cd week4 && PYTHONPATH=. pytest -v backend/tests --tb=short $ARGUMENTS
   ```

2. **If tests pass, generate coverage report**
   ```bash
   cd week4 && PYTHONPATH=. pytest --cov=backend --cov-report=term-missing backend/tests
   ```

3. **Run linting checks**
   ```bash
   cd week4 && make lint
   ```

## Expected Output

### On Success
- All tests pass with green checkmarks
- Coverage percentage for each file
- Lines not covered (Missing column)
- Lint check passes

### On Failure
- Failed test name and location (file:line)
- Error message and traceback
- Suggest specific fix based on error type

## Rollback/Safety
- Tests run against temporary SQLite database
- No production data is affected
- Safe to run repeatedly

## Examples
```
/tests                     # Run all tests
/tests -k notes            # Run only notes tests
/tests --lf                # Run last failed tests
/tests -x                  # Stop on first failure
```
