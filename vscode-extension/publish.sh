#!/bin/bash

# VS Code Extension Publishing Script
# This script helps you publish the extension to the VS Code Marketplace

set -e

echo "🚀 Publishing LLM Security Scanner VS Code Extension"
echo ""

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo "❌ vsce is not installed"
    echo "Installing vsce..."
    npm install -g @vscode/vsce
fi

# Compile TypeScript
echo "📦 Compiling TypeScript..."
npm run compile

# Package extension
echo "📦 Packaging extension..."
vsce package

# Get the generated VSIX filename
VSIX_FILE=$(ls -t *.vsix | head -1)

echo ""
echo "✅ Extension packaged: $VSIX_FILE"
echo ""
echo "Next steps:"
echo "1. Login to marketplace: vsce login spydra"
echo "2. Publish extension: vsce publish"
echo ""
echo "Or upload manually at: https://marketplace.visualstudio.com/manage"
echo ""
