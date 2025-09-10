# Rave MCP Server

A Model Context Protocol (MCP) server for marketing campaign management that integrates with Claude Desktop.

## Features

- **rave** - Simple greeting tool
- **start_campaign_creation** - Interactive campaign creation wizard
- **create_campaign** - Create marketing campaigns with required fields

## Setup

### 1. Install Dependencies
The server is a standalone Python script with no external dependencies (uses only Python standard library).

### 2. Configure Claude Desktop
Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "rave": {
      "command": "/Users/alex/Documents/Projects/rave/rave-mcp",
      "args": []
    }
  }
}
```

### 3. Restart Claude Desktop
Restart Claude Desktop to load the new MCP server.

## Usage

In Claude Desktop:
- **"rave"** - Get a greeting
- **"rave, start campaign creation"** - Start interactive campaign setup
- **"create campaign"** - Create a campaign (will prompt for required fields)

## Development

The MCP server implements JSON-RPC 2.0 protocol and handles:
- `initialize` - Server initialization
- `tools/list` - List available tools
- `tools/call` - Execute tool functions
- `prompts/list` - List prompts (returns empty)
- `resources/list` - List resources (returns empty)
- `notifications/initialized` - Handle initialization notifications

## Files

- `rave-mcp` - Main MCP server executable
- `README.md` - This documentation

## Future Enhancements

Based on the project design document, planned features include:
- Integration with external APIs (Google Ads, Email platforms)
- AWS Lambda deployment
- OAuth 2.1 authentication
- Campaign tracking and analytics