# Rave MCP Server - Installation Guide

## 📹 Video Walkthrough
**Installation video**: [video link goes here]

## Overview
The Rave MCP Server enables physician distribution map creation through Claude Desktop. This single binary works on both Windows and macOS.

---

## 🖥️ Windows Installation

### Step 1: Download and Save
1. Download `rave-mcp-go.exe` from Slack/internal distribution
2. Create a folder: `C:\Program Files\Rave\` (or your preferred location)
3. Save `rave-mcp-go.exe` in this folder

### Step 2: Update Claude Desktop Configuration
1. Press `Win + R`, type: `%APPDATA%\Claude\`
2. Open `claude_desktop_config.json` in a text editor
3. Add the Rave server configuration:

```json
{
  "mcpServers": {
    "rave": {
      "command": "C:\\Program Files\\Rave\\rave-mcp-go.exe",
      "args": [],
      "env": {
        "RAVE_API_KEY": "1234"
      }
    }
  }
}
```

**Note**: Use double backslashes (`\\`) in Windows paths, and adjust the path to where you saved the file.

### Step 3: Restart Claude Desktop
Close and restart Claude Desktop completely for changes to take effect.

### Step 4: Verify Installation
1. Double-click `rave-mcp-go.exe` to run diagnostics
2. **If Windows SmartScreen appears**: Click "More info" → "Run anyway" (first time only)
3. A popup should show "✅ Configuration validation complete!"

---

## 🍎 macOS Installation

### Step 1: Download and Save
1. Download `rave-mcp-go` from Slack/internal distribution
2. Create a folder: `/Applications/Rave/` or `~/Applications/Rave/`
3. Save `rave-mcp-go` in this folder

### Step 2: Clear Security Quarantine (if needed)
If downloaded from Slack/web, run this in Terminal:
```bash
xattr -cr /Applications/Rave/rave-mcp-go
```

### Step 3: Update Claude Desktop Configuration
1. Open Finder, press `Cmd + Shift + G`
2. Go to: `~/Library/Application Support/Claude/`
3. Open `claude_desktop_config.json` in a text editor
4. Add the Rave server configuration:

```json
{
  "mcpServers": {
    "rave": {
      "command": "/Applications/Rave/rave-mcp-go",
      "args": [],
      "env": {
        "RAVE_API_KEY": "1234"
      }
    }
  }
}
```

**Note**: Adjust the path to where you saved the file.

### Step 4: Restart Claude Desktop
Close and restart Claude Desktop completely for changes to take effect.

### Step 5: Verify Installation
1. Double-click `rave-mcp-go` to run diagnostics
2. **If security warning appears**: Right-click the file → "Open" → "Open" (first time only)
3. A terminal window and popup should show "✅ Configuration validation complete!"

---

## ✅ Verification & Usage

### Running Diagnostics
- **Windows**: Double-click `rave-mcp-go.exe`
- **macOS**: Double-click `rave-mcp-go`

### Success Indicators
✅ Config file exists  
✅ Config file has valid JSON  
✅ mcpServers section found  
✅ Rave server configured  
✅ Rave MCP binary exists  
✅ API key configured correctly  

### Using Rave in Claude Desktop
Once installed, you can use these commands in Claude Desktop:

- `"rave create list with 1000 physicians"`
- `"rave create list with 2500 physicians in a 30 mile radius"`
- `"create campaign for ABC Corp"`

---

## 🔧 Troubleshooting

### Common Issues

**"Invalid API key" error**
- Check that `RAVE_API_KEY` is set to `"1234"` in your config
- Ensure no typos in the JSON

**"Command not found" or binary not launching**
- Verify the file path in your config matches where you saved the binary
- On Windows: Use double backslashes (`\\`) in paths
- On macOS: Make sure you cleared quarantine with `xattr -cr`

**JSON syntax errors**
- Use an online JSON validator to check your config
- Ensure commas are placed correctly between multiple MCP servers

### Still Having Issues?
1. Run diagnostics by double-clicking the binary
2. The popup will show exactly what's wrong
3. Follow the specific instructions provided

---

## 📋 Sample Complete Config

If you have other MCP servers, your complete config might look like:

```json
{
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": ["basic-memory", "mcp"]
    },
    "rave": {
      "command": "/path/to/your/rave-mcp-go",
      "args": [],
      "env": {
        "RAVE_API_KEY": "1234"
      }
    }
  }
}
```

---

## 🚀 Ready to Use!

Once everything is configured, you can create physician distribution maps directly through Claude Desktop. The maps will be generated and uploaded to S3 with clickable links for easy access.

**Need help?** Contact your IT administrator or check the video walkthrough above.