# SubAgents Configuration

This directory contains SubAgent definitions for the Week 4 project.
SubAgents are specialized AI assistants that work together on specific tasks.

## Available SubAgents

1. **TestAgent** (`test-agent.md`) - Writes and validates tests
2. **CodeAgent** (`code-agent.md`) - Implements code to pass tests

## Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   User Request  │────▶│   TestAgent     │────▶│   CodeAgent     │
│  "Add feature"  │     │ Writes tests    │     │ Implements code │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                        │
                                ▼                        ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │  Tests fail     │     │  Tests pass     │
                        │  (expected)     │     │  (success!)     │
                        └─────────────────┘     └─────────────────┘
```

## Usage

To use the SubAgent workflow, invoke them in sequence:
1. First, activate TestAgent to write tests
2. Then, activate CodeAgent to implement the feature
3. Finally, TestAgent verifies the implementation
