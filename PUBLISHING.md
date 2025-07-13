# Publishing Guide

## 🚀 How to Publish semaphore-mcp to PyPI

### Prerequisites

1. **PyPI Account**: Create accounts on both [TestPyPI](https://test.pypi.org) and [PyPI](https://pypi.org)
2. **GitHub Repository**: Ensure your repo is public and the workflows are enabled
3. **Repository Secrets**: Configure the following in GitHub Settings > Secrets

### Step 1: Configure GitHub Repository Settings

#### Required Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

#### Set up PyPI Trusted Publishing
1. Go to [PyPI Trusted Publishing](https://pypi.org/manage/account/publishing/)
2. Add a new publisher with these settings:
   - **Repository name**: `yourusername/semaphore-mcp`
   - **Workflow filename**: `publish.yml`
   - **Environment name**: `pypi`

### Step 2: Update Repository URLs

Edit `pyproject.toml` and replace the GitHub URLs:
```toml
[project.urls]
"Homepage" = "https://github.com/YOURUSERNAME/semaphore-mcp"
"Bug Tracker" = "https://github.com/YOURUSERNAME/semaphore-mcp/issues"
"Documentation" = "https://github.com/YOURUSERNAME/semaphore-mcp#readme"
"Source Code" = "https://github.com/YOURUSERNAME/semaphore-mcp"
```

### Step 3: Test Build Locally

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the build
twine check dist/*

# Test upload to TestPyPI (optional)
twine upload --repository testpypi dist/*
```

### Step 4: Create a Release

#### Manual Release Process
```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.1.0"

# 3. Create and push tag
git tag v0.1.0
git push origin v0.1.0
```

#### This will automatically:
- Trigger the GitHub Actions workflow
- Build the package
- Upload to PyPI using trusted publishing
- Create a GitHub release

### Step 5: Verify Publication

After the workflow completes:

1. Check [PyPI package page](https://pypi.org/project/semaphore-mcp/)
2. Test installation: `pip install semaphore-mcp`
3. Verify command works: `semaphore-mcp --help`

## 🔄 Release Workflow

### For Regular Updates

1. **Make changes** and commit to `main` branch
2. **Run tests** - ensure all tests pass
3. **Update version** in `pyproject.toml`
4. **Create tag** and push:
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```
5. **Monitor workflow** - check GitHub Actions for success
6. **Verify deployment** - test installation from PyPI

### Version Numbering

Use [Semantic Versioning](https://semver.org/):
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features (backward compatible)
- `1.0.0` - Stable release or breaking changes

## 🛠️ Publishing Checklist

Before creating a release:

- [ ] All tests pass locally and in CI
- [ ] Documentation is up to date
- [ ] Version number is updated in `pyproject.toml`
- [ ] CHANGELOG or release notes are prepared
- [ ] GitHub repository URLs are correct
- [ ] PyPI trusted publishing is configured
- [ ] Test with TestPyPI first (recommended)

## 🔧 Troubleshooting

### Common Issues

**Build fails**:
- Check `pyproject.toml` syntax
- Ensure all dependencies are specified
- Verify Python version compatibility

**Upload fails**:
- Verify PyPI trusted publishing setup
- Check GitHub secrets are configured
- Ensure tag format matches workflow trigger (`v*`)

**Package not found after upload**:
- Wait a few minutes for PyPI indexing
- Check package name spelling
- Verify upload actually succeeded in workflow logs

## 📋 Post-Publication Tasks

After successful publication:

1. **Update README** - Add PyPI installation badges
2. **Announce** - Share on relevant communities
3. **Monitor** - Watch for issues and user feedback
4. **Document** - Update any integration guides
5. **Plan next release** - Based on user feedback and needs

## 🏷️ Badges for README

Add these to your README after publishing:

```markdown
[![PyPI version](https://badge.fury.io/py/semaphore-mcp.svg)](https://badge.fury.io/py/semaphore-mcp)
[![Downloads](https://pepy.tech/badge/semaphore-mcp)](https://pepy.tech/project/semaphore-mcp)
[![Python Versions](https://img.shields.io/pypi/pyversions/semaphore-mcp.svg)](https://pypi.org/project/semaphore-mcp/)
```