# LLM Security Scanner - Visual Studio Extension

A Visual Studio extension that integrates the LLM Security Scanner to detect AI/LLM-specific security vulnerabilities in your Python code.

## Features

- 🔍 **Automatic Scanning**: Scans files automatically on save
- ⚠️ **Error List Integration**: Shows vulnerabilities in Visual Studio's Error List
- 🎯 **OWASP Top 10 Coverage**: Detects all OWASP LLM Top 10 vulnerabilities
- 📊 **Severity Filtering**: Shows findings by severity (Critical, High, Medium, Low)
- 🚀 **Workspace Scanning**: Scan entire workspace with a single command
- 💡 **Remediation Guidance**: Shows remediation suggestions for each finding

## Requirements

- Visual Studio 2022 (17.0 or later)
- Python 3.11+ installed
- LLM Security Scanner Python package installed (`pip install -e .` from project root)

## Building the Extension

### Prerequisites

1. Install Visual Studio 2022 with:
   - Visual Studio extension development workload
   - .NET desktop development workload
   - Python development workload

2. Install Visual Studio SDK (included with extension development workload)

### Build Steps

1. **Open the project in Visual Studio:**
   ```bash
   cd visual-studio-extension
   # Open LLMSecurityScanner.sln in Visual Studio
   ```

2. **Restore NuGet packages:**
   - Right-click solution → Restore NuGet Packages

3. **Build the project:**
   - Build → Build Solution (Ctrl+Shift+B)
   - This creates a `.vsix` file in `bin\Debug\` or `bin\Release\`

## Installation

### Development Installation

1. Build the project in Debug mode
2. Press F5 to start Visual Studio Experimental Instance
3. The extension will be loaded in the experimental instance

### Production Installation

1. Build the project in Release mode
2. Locate the `.vsix` file in `bin\Release\`
3. Double-click the `.vsix` file to install
4. Or use: `Tools → Extensions and Updates → Install from VSIX`

## Configuration

The extension uses the following settings (can be configured via Visual Studio Options):

- **Python Path**: Path to Python interpreter (default: `python3`)
- **Rules Directory**: Path to custom rules directory (optional)
- **Auto-scan on Save**: Automatically scan files when saved (default: true)

## Usage

### Automatic Scanning

The extension automatically scans Python files when:
- A file is saved
- A workspace is opened
- A file is opened (if enabled)

### Manual Scanning

1. Right-click on a file or folder in Solution Explorer
2. Select "Scan with LLM Security Scanner"
3. Results appear in the Error List

### Viewing Results

1. Open **View → Error List** (Ctrl+\\, E)
2. Filter by "LLM Security Scanner" if needed
3. Click on a finding to navigate to the code location
4. View remediation guidance in the Error List details

## Troubleshooting

### Extension Not Loading

1. Check Visual Studio version (requires 17.0+)
2. Verify Visual Studio SDK is installed
3. Check Output window for error messages

### Scanner Not Found

1. Verify Python is installed: `python3 --version`
2. Verify LLM scanner is installed: `python3 -m llm_scan.runner --help`
3. Check Python path in extension settings

### No Findings Appearing

1. Verify the file contains LLM-related code
2. Check Error List filters (may be filtered out)
3. Check Output window for scanner errors

## Development

### Project Structure

```
visual-studio-extension/
├── LLMSecurityScanner.csproj      # Project file
├── source.extension.vsixmanifest   # Extension manifest
├── LLMSecurityScannerPackage.cs    # Main package class
├── Services/
│   ├── ScannerService.cs          # Calls Python scanner
│   └── ErrorListService.cs        # Updates Error List
├── Models/
│   ├── Finding.cs                 # Finding model
│   └── ScanResult.cs              # Scan result model
└── Properties/
    └── AssemblyInfo.cs            # Assembly metadata
```

### Key Components

- **LLMSecurityScannerPackage**: Main package that initializes the extension
- **ScannerService**: Executes Python scanner and parses JSON results
- **ErrorListService**: Converts findings to Visual Studio Error List tasks

## License

See LICENSE file in project root.

## Contributing

Contributions welcome! Please see the main project README for contribution guidelines.
