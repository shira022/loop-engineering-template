## Description

<!-- Briefly describe the changes in this PR -->

## Related Issue

<!-- Fixes #123 -->

## Branch Type

- [ ] **feature -> develop** : 新機能追加
- [ ] **release -> main / develop** : リリース準備
- [ ] **hotfix -> main / develop** : 緊急修正
- [ ] **develop -> main** : リリースマージ
- [ ] Other:

## Type of Change

- [ ] Bug fix
- [ ] New feature / New skill
- [ ] Documentation update
- [ ] CI / infrastructure
- [ ] Refactoring
- [ ] Security fix

## Checklist

### Common
- [ ] My changes follow the project's code style
- [ ] I have tested my changes locally
- [ ] Skills include valid YAML frontmatter
- [ ] Documentation has been updated as needed
- [ ] This PR does not break existing functionality
- [ ] Pre-commit hooks pass locally

### Testing (REQUIRED)
- [ ] **Tests are required for all new code.** Existing tests still pass.
- [ ] **Coverage**: New code has corresponding unit/integration tests
- [ ] **Edge Cases**: Tests cover error paths, boundary conditions
- [ ] **No-decrease**: Coverage does not drop below 80%
- [ ] **Regression**: Full test suite passes before submitting

### Branch-Specific
- [ ] [feature] Branch is up-to-date with develop (rebased)
- [ ] [release] Version number bumped, changelog updated
- [ ] [hotfix] Same fix applied to develop (or follow-up planned)
- [ ] [security] No credentials/tokens/secrets in diff

## Security Considerations

<!-- For security-related changes -->

## Additional Notes
