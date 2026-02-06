---
description: Run tests with coverage and summarize results for week4 project
---

# Run Tests Workflow

This workflow runs the test suite for the week4 project, generates a coverage report, and provides a summary with actionable next steps.

## Prerequisites
- Ensure you're in the week4 directory
- Python environment with pytest and pytest-cov installed

## Steps

// turbo-all

1. Navigate to week4 and run the test suite:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m pytest -v backend/tests --tb=short
```

2. If tests pass, run coverage report:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m pytest --cov=backend --cov-report=term-missing backend/tests
```

3. Run linting check to ensure code quality:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && make lint
```

## Expected Output

### On Success:
- All tests pass (green checkmarks)
- Coverage report showing percentage of code covered
- Lint check passes with no errors

### On Failure:
- Failed test details with file:line numbers
- Suggest fixes based on error messages
- Prioritize fixing tests in this order:
  1. Unit tests (`test_extract.py`)
  2. API tests (`test_notes.py`, `test_action_items.py`)

## Rollback/Safety Notes
- Tests run against a temporary SQLite database, not production data
- No destructive side effects
- Safe to run multiple times

## Arguments
- `$ARGUMENTS` can be used to pass additional pytest options
  - Example: `/run-tests -k test_notes` to run only notes tests
  - Example: `/run-tests --lf` to run only last failed tests
