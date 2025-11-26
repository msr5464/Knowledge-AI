#!/bin/bash
# Platform Detection Script
# Detects the operating system and provides platform-specific instructions

detect_platform() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

PLATFORM=$(detect_platform)

echo "========================================"
echo "Platform Detection"
echo "========================================"
echo "Detected Platform: $PLATFORM"
echo ""

case $PLATFORM in
    linux)
        echo "✅ Linux detected"
        echo ""
        echo "To install:"
        echo "  bash scripts/install.sh"
        echo ""
        echo "To run:"
        echo "  bash scripts/run.sh"
        ;;
    macos)
        echo "✅ macOS detected"
        echo ""
        echo "To install:"
        echo "  bash scripts/install.sh"
        echo ""
        echo "To run:"
        echo "  bash scripts/run.sh"
        ;;
    windows)
        echo "✅ Windows detected (Git Bash/Cygwin)"
        echo ""
        echo "For PowerShell:"
        echo "  .\scripts\install.ps1"
        echo "  .\scripts\run.ps1"
        echo ""
        echo "For Command Prompt:"
        echo "  scripts\install.bat"
        echo "  scripts\run.bat"
        ;;
    *)
        echo "⚠️  Unknown platform: $OSTYPE"
        echo ""
        echo "Please check DEPLOYMENT.md for manual installation instructions"
        ;;
esac

echo ""
echo "For detailed instructions, see DEPLOYMENT.md"

