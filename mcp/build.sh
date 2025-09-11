#!/bin/bash

echo "Building Rave MCP Server..."

# Build the Go binary
go build -o rave-mcp-go rave-mcp.go

if [ $? -eq 0 ]; then
    echo "✅ Binary built successfully: rave-mcp-go"
    
    # Create macOS app bundle for diagnostics (no terminal window)
    echo "Creating macOS app bundle..."
    
    mkdir -p "Rave MCP Diagnostics.app/Contents/MacOS"
    mkdir -p "Rave MCP Diagnostics.app/Contents/Resources"
    
    # Copy binary to app bundle
    cp rave-mcp-go "Rave MCP Diagnostics.app/Contents/MacOS/RaveMCPDiagnostics"
    chmod +x "Rave MCP Diagnostics.app/Contents/MacOS/RaveMCPDiagnostics"
    
    echo "✅ macOS app bundle created: Rave MCP Diagnostics.app"
    echo ""
    echo "📋 Usage:"
    echo "  • For MCP server: Use 'rave-mcp-go' in Claude Desktop config"
    echo "  • For diagnostics: Double-click 'Rave MCP Diagnostics.app' (no terminal)"
    echo ""
    echo "🚀 Ready for deployment!"
    
else
    echo "❌ Build failed!"
    exit 1
fi