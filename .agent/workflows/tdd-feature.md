---
description: Use TestAgent + CodeAgent SubAgents to implement a feature using TDD
---

# TDD Feature Workflow (SubAgents)

This workflow uses two specialized SubAgents to implement features following Test-Driven Development:
- **TestAgent**: Writes tests first
- **CodeAgent**: Implements code to pass tests

## Usage
```
/tdd-feature <feature description>
```

## Arguments
- `$ARGUMENTS` - Description of the feature to implement

## Workflow Steps

// turbo-all

### Phase 1: TestAgent - Write Tests

1. Read the TestAgent configuration:
```bash
cat /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4/.claude/subagents/test-agent.md
```

2. **[MANUAL]** As TestAgent, analyze the feature request and write failing tests in `backend/tests/`

3. Run tests to confirm they fail:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m pytest -v backend/tests --tb=short
```

### Phase 2: CodeAgent - Implement Feature

4. Read the CodeAgent configuration:
```bash
cat /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4/.claude/subagents/code-agent.md
```

5. **[MANUAL]** As CodeAgent, implement the feature to make tests pass

6. Run tests to verify implementation:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m pytest -v backend/tests --tb=short
```

7. Run lint check:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && make lint
```

### Phase 3: TestAgent - Verify & Report

8. Run coverage report:
```bash
cd /Users/boss_li12/Desktop/file/project_playground/modern-software-dev-assignments/week4 && PYTHONPATH=. /Users/boss_li12/miniforge3/bin/python -m pytest --cov=backend --cov-report=term-missing backend/tests
```

## Expected Output

### On Success:
```
## TDD Feature Implementation Complete

### TestAgent Phase
- Tests written: test_xxx, test_yyy
- Initial status: ❌ Failing (expected)

### CodeAgent Phase  
- Files modified: routers/xxx.py
- Implementation: [summary]
- Test status: ✅ All passing

### Verification
- Coverage: XX%
- Lint: ✅ Passed

### Feature Complete! 🎉
```

### On Failure:
- Report which phase failed
- Provide error details
- Suggest fixes

## Rollback Notes
- Tests are additive (can be deleted if needed)
- Code changes can be reverted with git
- No database schema changes in this workflow

## Example
```
/tdd-feature Add PUT /notes/{id} endpoint to update note title and content
```
