# 🚀 Automated Release Guide

## Quick Release Process

The new automated release workflow makes releasing as simple as clicking a button in GitHub!

### How to Create a Release

1. **Go to GitHub Actions**
   - Navigate to your repository on GitHub
   - Click the "Actions" tab

2. **Select the Release Workflow**
   - Click on "Create Release" in the left sidebar
   - Click the "Run workflow" button (blue button on the right)

3. **Fill in Release Details**
   - **Version**: Enter the new version number (e.g., `0.1.6`, `1.0.0`)
     - Must follow semantic versioning: `MAJOR.MINOR.PATCH`
   - **Release type**: Select patch/minor/major (for documentation purposes)
   - **Pre-release**: Check this box if it's a beta/alpha release

4. **Click "Run workflow"**
   - The automation handles everything else!

### What Happens Automatically

The workflow will:
- ✅ Validate the version format
- ✅ Check that the version doesn't already exist
- ✅ Update the version in `pyproject.toml`
- ✅ Commit the version change to the main branch
- ✅ Create and push a git tag (e.g., `v0.1.6`)
- ✅ Generate release notes from recent commits
- ✅ Create a GitHub release
- ✅ Trigger the existing PyPI publishing workflow
- ✅ Deploy to TestPyPI first, then PyPI

### Monitoring the Release

1. **Watch the Workflow**: The "Create Release" workflow will show progress
2. **Check PyPI Publishing**: After the tag is created, the "Publish to PyPI" workflow will automatically start
3. **Verify Publication**: Check that your package appears on [PyPI](https://pypi.org/project/semaphore-mcp/)

### Version Numbering Guidelines

Follow [Semantic Versioning](https://semver.org/):
- **Patch** (0.1.5 → 0.1.6): Bug fixes, small improvements
- **Minor** (0.1.6 → 0.2.0): New features, backward compatible
- **Major** (0.2.0 → 1.0.0): Breaking changes, major milestones

### Pre-Release Versions

For testing releases:
- Use versions like `1.0.0-beta.1`, `1.0.0-rc.1`
- Check the "Pre-release" option
- These won't be marked as the "latest" release on GitHub

### Troubleshooting

**Common Issues:**
- **"Version already exists"**: Choose a different version number
- **"Invalid version format"**: Ensure format is `X.Y.Z` (e.g., `1.0.0`)
- **Workflow permissions**: Ensure Actions have write permissions in repository settings

**If Something Goes Wrong:**
1. Check the workflow logs in GitHub Actions
2. The workflow will stop safely if there are errors
3. No changes are made until all validations pass
4. You can always create releases manually if needed

## Manual Release (Alternative)

If you prefer the traditional approach:

```bash
# 1. Update version in pyproject.toml manually
# 2. Commit the change
git add pyproject.toml
git commit -m "Bump version to 0.1.6"

# 3. Create and push tag
git tag v0.1.6
git push origin v0.1.6

# The existing publish.yml workflow will trigger automatically
```

## Benefits of Automated Releases

- **Consistency**: Same process every time
- **Safety**: Validation prevents common mistakes
- **Automation**: No manual PyPI uploads or release notes
- **Traceability**: Clear commit history and release notes
- **Speed**: One-click releases from anywhere

Happy releasing! 🎉
