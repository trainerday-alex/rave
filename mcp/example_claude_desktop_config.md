# Claude Desktop Configuration for Rave MCP Server

This document shows how to configure Claude Desktop to use the Rave MCP server.

## Configuration File Location

The Claude Desktop configuration file is located at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

## Example Configuration

Add the following to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "rave": {
      "command": "/path/to/your/rave/mcp/rave-mcp",
      "args": []
    }
  }
}
```

## Full Example with Multiple MCP Servers

If you have other MCP servers configured, your full config might look like:

```json
{
  "globalShortcut": "",
  "mcpServers": {
    "basic-memory": {
      "command": "uvx",
      "args": [
        "basic-memory",
        "mcp"
      ]
    },
    "rave": {
      "command": "/Users/yourusername/Documents/Projects/rave/mcp/rave-mcp",
      "args": []
    }
  },
  "preferences": {
    "menuBarEnabled": false
  }
}
```

## Setup Steps

1. **Clone/Download this repository** to your desired location
2. **Make the MCP server executable**:
   ```bash
   chmod +x /path/to/rave/mcp/rave-mcp
   ```
3. **Update the path** in the configuration above to match your actual file location
4. **Add the configuration** to your `claude_desktop_config.json` file
5. **Restart Claude Desktop** for changes to take effect

## Available Tools

Once configured, the Rave MCP server provides these tools in Claude Desktop:

- **`rave`** - Simple greeting tool
- **`start_campaign_creation`** - Interactive campaign creation wizard
- **`create_campaign`** - Create marketing campaigns with required fields

## Usage Examples

In Claude Desktop, you can use:
- *"rave"* - Get a greeting from the server
- *"rave, start campaign creation"* - Begin interactive campaign setup
- *"Create a campaign for client ABC Corp"* - Direct campaign creation

## Troubleshooting

### Server Not Appearing
- Verify the file path in the configuration is correct
- Ensure the `rave-mcp` file is executable (`chmod +x`)
- Check Claude Desktop logs at `~/Library/Logs/Claude/`

### Permission Issues
- Make sure the `rave-mcp` script has execute permissions
- Verify the path is accessible to Claude Desktop

### Configuration Errors
- Validate your JSON syntax using a JSON validator
- Ensure commas are properly placed between multiple MCP servers
- Check that the file path uses forward slashes and is absolute

## Future Installation Script

A future installation script will:
1. Automatically detect your system and Claude Desktop config location
2. Copy the MCP server to an appropriate location
3. Update your Claude Desktop configuration
4. Handle permissions and path setup
5. Validate the installation

For now, manual configuration using this guide is required.