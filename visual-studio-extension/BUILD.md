# Building the Visual Studio Extension

## Prerequisites

1. **Visual Studio 2022** (17.0 or later) with:
   - **Visual Studio extension development** workload
   - **.NET desktop development** workload
   - **Python development** workload (optional, for testing)

2. **Visual Studio SDK** (automatically installed with extension development workload)

3. **Python 3.11+** with LLM Security Scanner installed:
   ```bash
   # From project root
   pip install -e .
   pip install semgrep
   ```

## Build Steps

### Option 1: Build from Visual Studio

1. **Open the solution:**
   ```bash
   cd visual-studio-extension
   # Double-click LLMSecurityScanner.sln or open in Visual Studio
   ```

2. **Restore NuGet packages:**
   - Right-click solution → **Restore NuGet Packages**
   - Or: Build → **Restore NuGet Packages**

3. **Build the project:**
   - Build → **Build Solution** (Ctrl+Shift+B)
   - Or: Right-click project → **Build**

4. **Output:**
   - `.vsix` file created in `bin\Debug\` or `bin\Release\`
   - Example: `bin\Debug\LLMSecurityScanner.vsix`

### Option 2: Build from Command Line

```bash
cd visual-studio-extension

# Restore packages
dotnet restore LLMSecurityScanner.csproj

# Build (requires MSBuild)
msbuild LLMSecurityScanner.csproj /p:Configuration=Release
```

## Testing the Extension

### Development Testing (Experimental Instance)

1. **Set as startup project:**
   - Right-click `LLMSecurityScanner` project → **Set as StartUp Project**

2. **Press F5** or **Debug → Start Debugging**
   - This launches Visual Studio Experimental Instance
   - Extension is automatically loaded

3. **Test in Experimental Instance:**
   - Open a Python project
   - The extension should activate automatically
   - Try scanning a file

### Production Installation

1. **Build in Release mode:**
   - Configuration → **Release**
   - Build → **Build Solution**

2. **Install the VSIX:**
   - Double-click `bin\Release\LLMSecurityScanner.vsix`
   - Or: **Tools → Extensions and Updates → Install from VSIX**

3. **Restart Visual Studio**

## Troubleshooting

### Build Errors

**Error: "Microsoft.VisualStudio.SDK not found"**
- Install Visual Studio extension development workload
- Verify Visual Studio SDK is installed

**Error: "VSToolsPath not found"**
- Ensure you're building from Visual Studio (not just MSBuild)
- Or set VSToolsPath environment variable

**Error: "Newtonsoft.Json not found"**
- Restore NuGet packages: Right-click solution → Restore NuGet Packages

### Runtime Errors

**Extension doesn't load:**
- Check Visual Studio version (requires 17.0+)
- Check Output window for errors
- Verify extension is enabled: **Tools → Extensions and Updates**

**Scanner not found:**
- Verify Python is in PATH: `python3 --version`
- Verify scanner is installed: `python3 -m llm_scan.runner --help`
- Check Python path in extension settings

## Project Structure

```
visual-studio-extension/
├── LLMSecurityScanner.csproj      # C# project file
├── LLMSecurityScanner.sln         # Solution file
├── source.extension.vsixmanifest  # Extension manifest
├── LLMSecurityScannerPackage.cs   # Main package (entry point)
├── Services/
│   ├── ScannerService.cs         # Calls Python scanner
│   └── ErrorListService.cs       # Updates Error List
├── Models/
│   ├── Finding.cs                # Finding data model
│   └── ScanResult.cs             # Scan result model
├── Commands/
│   └── ScanWorkspaceCommand.cs   # Menu command handler
└── Properties/
    └── AssemblyInfo.cs           # Assembly metadata
```

## Next Steps

After building:

1. **Test the extension** in Experimental Instance (F5)
2. **Package for distribution** (build in Release mode)
3. **Create installer** or publish to Visual Studio Marketplace

## Publishing to Marketplace

1. Build in Release mode
2. Create a VSIX package
3. Sign up for Visual Studio Marketplace
4. Upload the VSIX file
5. Fill in extension metadata
