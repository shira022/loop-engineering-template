# Testing Policy

All projects from this template MUST have comprehensive test coverage.

## Principles

1. **Tests are not optional.** Every feature must include tests.
2. **Coverage minimum:** 80% line coverage (enforced in CI).
3. **Test types required:**
   - Unit tests for all modules
   - Edge case / boundary tests
   - Error path tests
   - Integration tests where applicable
4. **CI fails** if tests fail or coverage drops below threshold.

## Python

- Framework: pytest
- Coverage: pytest-cov
- Location: `tests/test_*.py`
- Patterns: fixtures, parametrize, mocking (unittest.mock)
- Run: `pytest tests/ --cov=src --cov-fail-under=80`

## TypeScript / Node.js

- Framework: vitest (preferred) or jest
- Coverage: vitest --coverage
- Location: `tests/**/*.test.ts`
- Run: `npm test`

## Rust

- Framework: built-in `#[test]`
- Location: inline + `tests/`
- Run: `cargo test`

## Go

- Framework: testing package
- Coverage: go test -cover
- Location: `*_test.go`
- Run: `go test ./...`

## CI Enforcement

The CI `build-and-test` job:
- Fails if no tests found (exit code 1)
- Fails if coverage below 80%
- Fails if any test fails

See `tests/test_example.py` and `tests/ts/` for patterns.
