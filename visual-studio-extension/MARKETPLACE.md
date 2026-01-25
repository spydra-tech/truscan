# Publishing to Visual Studio Marketplace

This guide walks you through publishing the LLM Security Scanner extension to the Visual Studio Marketplace.

## Prerequisites

1. **Visual Studio Partner account** (free)
   - Sign up at: https://marketplace.visualstudio.com/manage
   - Use your Microsoft account or GitHub account

2. **Built VSIX file**
   - Build using GitHub Actions (recommended) or Windows machine
   - VSIX file should be in `bin/Release/LLMSecurityScanner.vsix`

3. **Extension metadata ready**
   - Display name, description, tags
   - Icon and preview images
   - License file

## Step 1: Prepare Extension Assets

### Required Files

1. **Icon**: `Resources/icon.png`
   - Size: 128x128 pixels
   - Format: PNG
   - Transparent background recommended

2. **Preview Image**: `Resources/preview.png`
   - Size: 533x324 pixels (recommended)
   - Format: PNG
   - Shows extension features

3. **License**: `LICENSE.txt` (in extension root)
   - Add your license text

### Update Manifest

Ensure `source.extension.vsixmanifest` has:
- Correct publisher name
- Version number
- Description
- Tags
- Categories

## Step 2: Build VSIX

### Option A: GitHub Actions (Recommended)

1. Push changes to trigger workflow
2. Go to **Actions** tab in GitHub
3. Find "Build Visual Studio Extension" workflow
4. Download the VSIX artifact

### Option B: Local Build (Windows)

```bash
cd visual-studio-extension
msbuild LLMSecurityScanner.csproj /p:Configuration=Release
```

VSIX will be in `bin/Release/LLMSecurityScanner.vsix`

## Step 3: Create Publisher Account

1. Go to: https://marketplace.visualstudio.com/manage
2. Sign in with Microsoft/GitHub account
3. Click **Create Publisher**
4. Fill in:
   - **Publisher ID**: Unique identifier (e.g., `llm-security`)
   - **Publisher Name**: Display name (e.g., "LLM Security")
   - **Description**: Brief description
   - **Support URL**: Your support page
5. Click **Create**

## Step 4: Upload Extension

1. Go to: https://marketplace.visualstudio.com/manage
2. Click **+ New Extension**
3. Select **Visual Studio**
4. Upload your `.vsix` file
5. Fill in extension details:

### Basic Information
- **Name**: LLM Security Scanner
- **Version**: 1.0.0
- **Description**: 
  ```
  Detect AI/LLM-specific security vulnerabilities in your Python code. 
  Integrates with Visual Studio's Error List to show findings from the 
  LLM Security Scanner based on OWASP Top 10 for LLM Applications.
  ```

### Categories
- Security
- Code Analysis

### Tags
- security
- llm
- ai
- vulnerability
- scanning
- owasp
- python

### Images
- Upload icon (128x128)
- Upload preview image (533x324)

### Links
- **Repository**: Your GitHub repo URL
- **Support**: Support page URL
- **License**: License file URL

## Step 5: Review and Publish

1. **Review** all information
2. Click **Save & Publish**
3. Extension goes through validation (usually 5-10 minutes)
4. Once approved, it's live on the marketplace!

## Step 6: Update Extension

For future updates:

1. **Update version** in:
   - `source.extension.vsixmanifest`
   - `Properties/AssemblyInfo.cs`

2. **Build new VSIX**

3. Go to marketplace → Your extension → **Update**

4. Upload new VSIX file

5. Add **Release notes** describing changes

6. Click **Save & Publish**

## Marketplace Guidelines

### Content Requirements
- Clear, accurate description
- Screenshots showing functionality
- Proper categorization
- Valid license

### Technical Requirements
- VSIX must be valid and installable
- Extension must not crash Visual Studio
- Must follow Visual Studio extension guidelines
- Must not violate Microsoft policies

### Review Process
- Initial review: 5-10 minutes
- Updates: Usually faster
- May require changes if issues found

## Best Practices

1. **Versioning**: Use semantic versioning (1.0.0, 1.1.0, 2.0.0)
2. **Release Notes**: Always include what's new/fixed
3. **Testing**: Test thoroughly before publishing
4. **Documentation**: Provide clear README and docs
5. **Support**: Respond to user feedback and issues

## Troubleshooting

### Extension Rejected
- Check email for rejection reason
- Fix issues and resubmit
- Common issues: crashes, policy violations, missing info

### Build Fails
- Check GitHub Actions logs
- Verify all dependencies are included
- Test VSIX installation locally first

### Installation Issues
- Test VSIX in Visual Studio Experimental Instance
- Verify all prerequisites are documented
- Check for missing dependencies

## Resources

- [Visual Studio Marketplace](https://marketplace.visualstudio.com/)
- [Extension Publishing Overview](https://docs.microsoft.com/en-us/visualstudio/extensibility/shipping-visual-studio-extensions)
- [VSIX Manifest Schema](https://docs.microsoft.com/en-us/visualstudio/extensibility/vsix-extension-schema-2-0-reference)
- [Extension Guidelines](https://docs.microsoft.com/en-us/visualstudio/extensibility/extension-gallery)

## Checklist Before Publishing

- [ ] Extension builds successfully
- [ ] VSIX installs and works in Visual Studio
- [ ] All required assets (icon, preview) are included
- [ ] Manifest has correct metadata
- [ ] Version number is set correctly
- [ ] License file is included
- [ ] Description is clear and accurate
- [ ] Tags and categories are appropriate
- [ ] Repository/support links are valid
- [ ] Extension tested in Visual Studio 2022
- [ ] No crashes or critical bugs
- [ ] Documentation is complete

## Next Steps After Publishing

1. **Monitor reviews** and ratings
2. **Respond to issues** and feedback
3. **Plan updates** based on user needs
4. **Promote** your extension (blog posts, social media)
5. **Maintain** and improve over time
