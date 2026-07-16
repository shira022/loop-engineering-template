# Testing Policy

All projects created from this template must have comprehensive test coverage, regardless of language or framework.

## Principles

1. **Tests are mandatory.** Every feature must have tests.
2. **Minimum coverage:** 80% line coverage (enforced by CI).
3. **Required test types:**
   - Unit tests — every module/function
   - Edge cases — empty input, null/None, boundary values
   - Error paths — exceptions, error returns, failure states
   - Integration tests — external services, database operations (if applicable)
4. **CI fails** when tests fail or coverage drops below threshold.

## Language-Specific Configuration

This template itself is language-agnostic. When you bootstrap a project using `project-bootstrapper`, the test configuration is dynamically generated based on your language/framework choice.

### Python (pytest)
```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

# CI coverage threshold
[tool.coverage.run]
source = ["src"]

[tool.coverage.report]
fail_under = 80
```

### TypeScript (vitest)
```ts
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json'],
      lines: 80,
    },
  },
});
```

### Rust (cargo-tarpaulin)
```toml
# In CI: cargo tarpaulin --out Xml --exclude-files tests/
```

### Go
```bash
# In CI: go test -coverprofile=coverage.out -covermode=count ./...
```

## CI Enforcement

The CI pipeline fails when:
- No tests are found
- Coverage is below 80%
- Tests fail

## References

- `test-policy` skill — agent-enforced test policy
- `project-bootstrapper` — generates CI config during project setup
- `.github/workflows/ci.yml` — CI configuration (generated per project)

---

## 🇯🇵 日本語

このテンプレートから作成されたプロジェクトは、言語・フレームワークを問わず包括的なテストカバレッジを持つ必要があります。原則: テスト必須、カバレッジ80%以上、ユニット/エッジケース/エラーパス/結合テストの4種必須。
