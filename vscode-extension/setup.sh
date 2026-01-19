#!/bin/bash
# Quick setup script for LLM Security Scanner VS Code Extension

set -e

echo "🔧 Setting up LLM Security Scanner VS Code Extension..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the vscode-extension directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
npm run compile

# Check if compilation succeeded
if [ ! -f "out/extension.js" ]; then
    echo "❌ Error: Compilation failed. out/extension.js not found."
    exit 1
fi

echo "✅ Extension compiled successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Open this folder in VS Code: code ."
echo "   2. Press F5 to launch Extension Development Host"
echo "   3. In the new window, open your workspace with Python files"
echo ""
echo "   OR"
echo ""
echo "   1. Package extension: vsce package"
echo "   2. Install: code --install-extension llm-security-scanner-1.0.0.vsix"
echo ""
