# Publishing to VS Code Marketplace

This guide walks you through publishing the LLM Security Scanner extension to the VS Code Marketplace.

## Prerequisites

1. **Microsoft/Azure account** or **GitHub account**
   - Sign up at: https://marketplace.visualstudio.com/manage
   - Use your Microsoft account or GitHub account

2. **vsce (VS Code Extension Manager)**
   ```bash
   npm install -g @vscode/vsce
   ```

3. **Personal Access Token (PAT)**
   - For publishing, you'll need a Personal Access Token
   - Go to: https://dev.azure.com → User Settings → Personal Access Tokens
   - Create a token with "Marketplace (Manage)" scope

## Step 1: Update package.json

Ensure your `package.json` has all required fields:

- ✅ `name`: Extension ID (lowercase, no spaces)
- ✅ `displayName`: Human-readable name
- ✅ `description`: Brief description
- ✅ `version`: Semantic version (e.g., 1.0.0)
- ✅ `publisher`: Your publisher ID (must match marketplace publisher)
- ✅ `engines.vscode`: Minimum VS Code version
- ✅ `categories`: At least one category
- ✅ `keywords`: Search keywords
- ✅ `repository`: GitHub repository URL (optional but recommended)
- ✅ `license`: License type
- ✅ `icon`: Extension icon (128x128 PNG)
- ✅ `galleryBanner`: Banner image (optional)

### Required Updates

Update these fields in `package.json`:

```json
{
  "publisher": "spydra",  // Your publisher ID (must match marketplace)
  "repository": {
    "type": "git",
    "url": "https://github.com/your-org/code-scan2.git"
  },
  "license": "MIT",
  "icon": "resources/icon.png",
  "galleryBanner": {
    "color": "#1e1e1e",
    "theme": "dark"
  }
}
```

## Step 2: Prepare Assets

### Required Files

1. **Icon**: `resources/icon.png`
   - Size: 128x128 pixels
   - Format: PNG
   - Transparent background recommended

2. **README.md**: Already exists - will be used as marketplace description

3. **CHANGELOG.md**: Already exists - tracks version history

4. **LICENSE**: Add license file (MIT, Apache, etc.)

### Optional Files

- `resources/gallery/` folder with screenshots
- `resources/preview.png` for marketplace preview

## Step 3: Create Publisher Account

1. Go to: https://marketplace.visualstudio.com/manage
2. Sign in with Microsoft/GitHub account
3. Click **Create Publisher**
4. Fill in:
   - **Publisher ID**: Unique identifier (e.g., `spydra`)
   - **Publisher Name**: Display name (e.g., "Spydra")
   - **Description**: Brief description
   - **Support URL**: Your support page
5. Click **Create**

**Important**: The `publisher` field in `package.json` must match your Publisher ID exactly!

## Step 4: Build and Package Extension

### Install vsce

```bash
npm install -g @vscode/vsce
```

### Update package.json

Make sure `package.json` has:
- Correct `publisher` (matches your marketplace publisher ID)
- Correct `version` (semantic versioning)
- All required metadata

### Package the Extension

```bash
cd vscode-extension

# Compile TypeScript
npm run compile

# Package extension
vsce package
```

This creates: `llm-security-scanner-1.0.0.vsix`

### Verify Package

```bash
# List package contents
vsce ls
```

## Step 5: Publish to Marketplace

### Option A: Publish via vsce (Recommended)

```bash
# Login to marketplace
vsce login <your-publisher-id>

# Publish extension
vsce publish
```

### Option B: Publish via Web UI

1. Go to: https://marketplace.visualstudio.com/manage
2. Click **+ New Extension**
3. Select **Visual Studio Code**
4. Upload your `.vsix` file
5. Fill in extension details
6. Click **Publish**

## Step 6: Update Extension

For future updates:

1. **Update version** in `package.json`:
   ```json
   "version": "1.0.1"
   ```

2. **Update CHANGELOG.md** with new changes

3. **Rebuild and republish**:
   ```bash
   npm run compile
   vsce package
   vsce publish
   ```

## Marketplace Guidelines

### Content Requirements
- Clear, accurate description
- Screenshots showing functionality (recommended)
- Proper categorization
- Valid license
- Privacy policy (if collecting data)

### Technical Requirements
- VSIX must be valid and installable
- Extension must not crash VS Code
- Must follow VS Code extension guidelines
- Must not violate Microsoft policies

### Review Process
- Initial review: Usually within 1-2 business days
- Updates: Usually faster (hours)
- May require changes if issues found

## Checklist Before Publishing

- [ ] `package.json` has correct `publisher` ID
- [ ] `package.json` has correct `version` (semantic versioning)
- [ ] `package.json` has `repository` URL
- [ ] `package.json` has `license` field
- [ ] Icon file exists (`resources/icon.png`, 128x128)
- [ ] README.md is complete and accurate
- [ ] CHANGELOG.md has version history
- [ ] Extension compiles without errors (`npm run compile`)
- [ ] Extension packages successfully (`vsce package`)
- [ ] Extension installs and works in VS Code
- [ ] All dependencies install correctly (semgrep auto-installs)
- [ ] Tested on different platforms (if applicable)
- [ ] No hardcoded paths or local dependencies
- [ ] Privacy policy added (if collecting user data)

## Publishing Commands Summary

```bash
# 1. Install vsce
npm install -g @vscode/vsce

# 2. Navigate to extension directory
cd vscode-extension

# 3. Compile
npm run compile

# 4. Package
vsce package

# 5. Login (first time only)
vsce login <publisher-id>

# 6. Publish
vsce publish

# Or publish specific version
vsce publish 1.0.0
```

## Troubleshooting

### "Publisher not found"
- Verify publisher ID in `package.json` matches marketplace publisher
- Make sure you're logged in: `vsce login <publisher-id>`

### "Extension already exists"
- Update version number in `package.json`
- Update CHANGELOG.md

### "Invalid package"
- Check for compilation errors: `npm run compile`
- Verify all required files are included
- Check `.vscodeignore` doesn't exclude required files

### Publishing Fails
- Check Personal Access Token has correct permissions
- Verify you're using the correct publisher account
- Check network connectivity

## Resources

- [VS Code Extension Marketplace](https://marketplace.visualstudio.com/vscode)
- [vsce Documentation](https://github.com/microsoft/vscode-vsce)
- [Extension Manifest](https://code.visualstudio.com/api/references/extension-manifest)
- [Publishing Extensions](https://code.visualstudio.com/api/working-with-extensions/publishing-extension)
- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Next Steps After Publishing

1. **Monitor reviews** and ratings
2. **Respond to issues** and feedback
3. **Plan updates** based on user needs
4. **Promote** your extension (blog posts, social media)
5. **Maintain** and improve over time
