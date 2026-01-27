# Publishing trusys-llm-scan to PyPI

This guide explains how to publish the `trusys-llm-scan` package to PyPI (Python Package Index) so users can install it with `pip install trusys-llm-scan`.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org) if you don't have one
2. **TestPyPI Account** (recommended): Create an account at [test.pypi.org](https://test.pypi.org) for testing
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI:
   - Go to Account Settings → API tokens
   - Create a new token with "Upload packages" scope
   - Save the tokens securely

## Setup GitHub Secrets

Add the following secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your TestPyPI API token (optional, for testing)

## Release Methods

### Method 1: Automated Release via GitHub Release (Recommended)

1. **Update version** in:
   - `setup.py` (line 10)
   - `pyproject.toml` (line 7)
   - `llm_scan/__init__.py` (line 3)

2. **Create a GitHub Release**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   
   Or create a release via GitHub UI:
   - Go to Releases → Draft a new release
   - Tag: `v1.0.0` (or your version)
   - Title: `Release v1.0.0`
   - Description: Release notes
   - Check "Set as the latest release"
   - Click "Publish release"

3. **The workflow will automatically**:
   - Build the package
   - Publish to PyPI
   - Upload build artifacts

### Method 2: Manual Workflow Dispatch

1. Go to Actions → "Publish to PyPI" workflow
2. Click "Run workflow"
3. Enter:
   - **Version**: e.g., `1.0.0`
   - **Publish to PyPI**: Choose `true` for PyPI or `false` for TestPyPI
4. Click "Run workflow"

### Method 3: Manual Local Build and Upload

If you prefer to build and upload manually:

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI (production)
twine upload dist/*
```

## Package Structure

The package includes:
- All Python modules in `llm_scan/`
- All rule files in `llm_scan/rules/`
- Entry point: `trusys-llm-scan` command (installed via `console_scripts`)

## Installation After Release

Users can install the package with:

```bash
pip install trusys-llm-scan
```

After installation, users can run:

```bash
trusys-llm-scan . --format console
```

Or use it as a Python module:

```bash
python -m llm_scan.runner . --format console
```

## Version Management

- Update version in three places:
  1. `setup.py`: `version="1.0.0"`
  2. `pyproject.toml`: `version = "1.0.0"`
  3. `llm_scan/__init__.py`: `__version__ = "1.0.0"`

- Follow [Semantic Versioning](https://semver.org/):
  - **MAJOR**: Breaking changes
  - **MINOR**: New features (backward compatible)
  - **PATCH**: Bug fixes

## Testing Before Release

1. **Test locally**:
   ```bash
   pip install -e .
   trusys-llm-scan --help
   ```

2. **Test on TestPyPI**:
   - Use workflow dispatch with `publish_to_pypi: false`
   - Install from TestPyPI:
     ```bash
     pip install --index-url https://test.pypi.org/simple/ trusys-llm-scan
     ```

3. **Verify package contents**:
   ```bash
   python -m build
   tar -tzf dist/trusys-llm-scan-*.tar.gz | head -20
   ```

## Troubleshooting

### Build fails with "package_data not found"
- Ensure `MANIFEST.in` includes all necessary files
- Check that rule files are included in `package_data` in `setup.py`

### Upload fails with "403 Forbidden"
- Verify API token is correct
- Check token has "Upload packages" scope
- Ensure package name is available (if first release)

### Version already exists
- PyPI doesn't allow re-uploading the same version
- Increment version number and try again

## Post-Release Checklist

- [ ] Verify package installs: `pip install trusys-llm-scan`
- [ ] Test command works: `trusys-llm-scan --help`
- [ ] Verify rules are included: Check `llm_scan/rules/` directory
- [ ] Update documentation with new version
- [ ] Announce release (if applicable)

## CI/CD Integration

The GitHub Actions workflow (`.github/workflows/publish-pypi.yml`) automatically:
- Builds the package on release
- Validates the package
- Publishes to PyPI
- Uses trusted publishing (no password needed if using PyPI API tokens)

## Additional Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Semantic Versioning](https://semver.org/)
