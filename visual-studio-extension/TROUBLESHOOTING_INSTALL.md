# Troubleshooting VSIX Installation

## Error: "Extract: extension/package.json not found inside zip"

This error occurs when Visual Studio tries to install the VSIX as a VS Code extension. This can happen for several reasons:

### Solution 1: Install in Visual Studio (Not VS Code)

**Important**: This is a **Visual Studio** extension, NOT a VS Code extension.

- ✅ Install in **Visual Studio 2022** (Community, Professional, or Enterprise)
- ❌ Do NOT install in VS Code

### Solution 2: Verify VSIX File Type

1. Check the file extension - it should be `.vsix`
2. Right-click the file → Properties
3. Ensure it's not corrupted or renamed

### Solution 3: Install via Visual Studio UI

1. Open **Visual Studio 2022**
2. Go to **Tools → Extensions and Updates**
3. Click **Install from VSIX...**
4. Select your `.vsix` file
5. Click **Install**
6. Restart Visual Studio

### Solution 4: Verify VSIX Contents

The VSIX should contain:
- `extension.vsixmanifest` (not `package.json`)
- `[Content_Types].xml`
- DLL files
- Resources folder
- LICENSE.txt

If you see `package.json` inside, it's a VS Code extension, not a Visual Studio extension.

### Solution 5: Rebuild the VSIX

If the VSIX is corrupted or incorrectly built:

1. Open the solution in Visual Studio 2022
2. Clean the solution: **Build → Clean Solution**
3. Rebuild: **Build → Rebuild Solution**
4. Check `bin\Release\LLMSecurityScanner.vsix`

### Solution 6: Check Visual Studio Version

Ensure you're using **Visual Studio 2022** (version 17.0 or later):
- Visual Studio 2019 or earlier won't work
- VS Code won't work (different extension format)

### Solution 7: Manual Installation via Command Line

```powershell
# Open Developer Command Prompt for VS 2022
cd "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE"
.\VSIXInstaller.exe "path\to\LLMSecurityScanner.vsix"
```

### Solution 8: Check for Conflicting Extensions

If you have a VS Code extension with a similar name, it might cause confusion. Uninstall any conflicting extensions first.

## Verification

After installation, verify the extension is loaded:

1. **Tools → Extensions and Updates**
2. Search for "LLM Security Scanner"
3. Should show as **Installed** and **Enabled**
4. Check **View → Other Windows → Output** for any errors

## Still Having Issues?

1. Check Visual Studio version: **Help → About Microsoft Visual Studio**
2. Verify you have Visual Studio extension development tools installed
3. Check the Output window for detailed error messages
4. Try installing in Visual Studio Experimental Instance first (F5 from the extension project)
