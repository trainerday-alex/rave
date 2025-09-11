package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"
)

type JsonRpcRequest struct {
	ID      int             `json:"id"`
	Method  string          `json:"method"`
	Params  json.RawMessage `json:"params,omitempty"`
}

type JsonRpcResponse struct {
	JsonRpc string      `json:"jsonrpc"`
	ID      int         `json:"id"`
	Result  interface{} `json:"result,omitempty"`
	Error   *JsonRpcError `json:"error,omitempty"`
}

type JsonRpcError struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
}

type Tool struct {
	Name        string      `json:"name"`
	Description string      `json:"description"`
	InputSchema interface{} `json:"inputSchema"`
}

type ToolCallParams struct {
	Name      string                 `json:"name"`
	Arguments map[string]interface{} `json:"arguments"`
}

type TextContent struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type ToolResult struct {
	Content []TextContent `json:"content"`
	IsError bool          `json:"isError,omitempty"`
}

func main() {
	// Check if we're being called by MCP (stdin has data) or double-clicked (interactive)
	stat, _ := os.Stdin.Stat()
	if (stat.Mode() & os.ModeCharDevice) != 0 {
		// Interactive mode - user double-clicked
		runDiagnostics()
		return
	}
	
	// MCP mode - handle JSON-RPC over stdin
	scanner := bufio.NewScanner(os.Stdin)
	
	for scanner.Scan() {
		line := scanner.Text()
		var request JsonRpcRequest
		
		if err := json.Unmarshal([]byte(line), &request); err != nil {
			sendError(0, -32700, "Parse error")
			continue
		}
		
		handleRequest(request)
	}
}

func handleRequest(request JsonRpcRequest) {
	switch request.Method {
	case "initialize":
		sendResponse(request.ID, map[string]interface{}{
			"protocolVersion": "2024-11-05",
			"capabilities": map[string]interface{}{
				"tools": map[string]bool{"listChanged": true},
			},
			"serverInfo": map[string]interface{}{
				"name":    "rave",
				"version": "1.0.0",
			},
		})
		
	case "notifications/initialized":
		// No response needed for notifications
		return
		
	case "tools/list":
		sendResponse(request.ID, handleListTools())
		
	case "tools/call":
		var params ToolCallParams
		if err := json.Unmarshal(request.Params, &params); err != nil {
			sendError(request.ID, -32602, "Invalid params")
			return
		}
		sendResponse(request.ID, handleCallTool(params.Name, params.Arguments))
		
	case "prompts/list":
		sendResponse(request.ID, map[string]interface{}{"prompts": []interface{}{}})
		
	case "resources/list":
		sendResponse(request.ID, map[string]interface{}{"resources": []interface{}{}})
		
	default:
		sendError(request.ID, -32601, "Method not found")
	}
}

func handleListTools() map[string]interface{} {
	tools := []Tool{
		{
			Name:        "rave",
			Description: "Says hello from Rave MCP server",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"name": map[string]interface{}{
						"type":        "string",
						"description": "Name to greet (optional, defaults to 'World')",
					},
				},
			},
		},
		{
			Name:        "start_campaign_creation",
			Description: "Start the interactive campaign creation process - will ask user for required information step by step",
			InputSchema: map[string]interface{}{
				"type":                 "object",
				"properties":           map[string]interface{}{},
				"additionalProperties": false,
			},
		},
		{
			Name:        "create_campaign",
			Description: "Create a new marketing campaign with all required information provided",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"campaign_name": map[string]interface{}{
						"type":        "string",
						"description": "Name of the campaign (required)",
					},
					"description": map[string]interface{}{
						"type":        "string",
						"description": "Campaign description (required)",
					},
					"client_name": map[string]interface{}{
						"type":        "string",
						"description": "Client name (required)",
					},
					"budget": map[string]interface{}{
						"type":        "number",
						"description": "Campaign budget (optional)",
					},
					"channels": map[string]interface{}{
						"type":        "array",
						"items":       map[string]string{"type": "string"},
						"description": "Marketing channels (e.g., email, social, ads)",
					},
				},
				"required": []string{"campaign_name", "description", "client_name"},
			},
		},
		{
			Name:        "create_list",
			Description: "Create a physician distribution map showing the specified number of physicians in a geographic area",
			InputSchema: map[string]interface{}{
				"type": "object",
				"properties": map[string]interface{}{
					"count": map[string]interface{}{
						"type":        "integer",
						"description": "Number of physicians to display (e.g., 1000)",
						"minimum":     10,
						"maximum":     10000,
					},
					"radius": map[string]interface{}{
						"type":        "integer",
						"description": "Radius in miles (optional, defaults to 50)",
						"minimum":     5,
						"maximum":     200,
					},
					"lat": map[string]interface{}{
						"type":        "number",
						"description": "Center latitude (optional, defaults to San Antonio)",
					},
					"lon": map[string]interface{}{
						"type":        "number",
						"description": "Center longitude (optional, defaults to San Antonio)",
					},
					"clusters": map[string]interface{}{
						"type":        "integer",
						"description": "Maximum number of clusters (optional, defaults to 50)",
						"minimum":     1,
						"maximum":     100,
					},
				},
				"required": []string{"count"},
			},
		},
	}
	
	return map[string]interface{}{"tools": tools}
}

func handleCallTool(name string, arguments map[string]interface{}) ToolResult {
	switch name {
	case "rave":
		greetingName := "World"
		if name, ok := arguments["name"].(string); ok {
			greetingName = name
		}
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("Hello %s! This is Rave MCP Server 🎉", greetingName),
			}},
		}
		
	case "start_campaign_creation":
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "🚀 Let's create a new campaign! I need some information from you:\n\n1. **Campaign Name**: What would you like to call this campaign?\n2. **Client Name**: Which client is this campaign for?\n3. **Description**: Can you describe what this campaign is about?\n\nOptionally, you can also provide:\n- **Budget**: What's the budget for this campaign?\n- **Channels**: Which marketing channels do you want to use? (e.g., email, social, google-ads, facebook-ads)\n\nOnce you provide these details, I'll create the campaign for you!",
			}},
		}
		
	case "create_campaign":
		return handleCreateCampaign(arguments)
		
	case "create_list":
		return handleCreateList(arguments)
		
	default:
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("Unknown tool: %s", name),
			}},
			IsError: true,
		}
	}
}

func handleCreateCampaign(arguments map[string]interface{}) ToolResult {
	campaignName := getString(arguments, "campaign_name")
	description := getString(arguments, "description")
	clientName := getString(arguments, "client_name")
	
	if campaignName == "" {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "❌ Campaign name is required. Please ask the user: What would you like to name this campaign?",
			}},
			IsError: true,
		}
	}
	
	if description == "" {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "❌ Campaign description is required. Please ask the user: Can you describe what this campaign is about?",
			}},
			IsError: true,
		}
	}
	
	if clientName == "" {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "❌ Client name is required. Please ask the user: Which client is this campaign for?",
			}},
			IsError: true,
		}
	}
	
	responseText := fmt.Sprintf("Campaign Created Successfully! 🎉\n\nCampaign Details:\n• Name: %s\n• Client: %s\n• Description: %s", campaignName, clientName, description)
	
	if budget, ok := arguments["budget"].(float64); ok {
		responseText += fmt.Sprintf("\n• Budget: $%.2f", budget)
	}
	
	if channels, ok := arguments["channels"].([]interface{}); ok && len(channels) > 0 {
		channelStrs := make([]string, len(channels))
		for i, ch := range channels {
			if str, ok := ch.(string); ok {
				channelStrs[i] = str
			}
		}
		responseText += fmt.Sprintf("\n• Channels: %v", channelStrs)
	}
	
	responseText += "\n\n✅ Campaign is ready for launch!"
	
	return ToolResult{
		Content: []TextContent{{
			Type: "text",
			Text: responseText,
		}},
	}
}

func handleCreateList(arguments map[string]interface{}) ToolResult {
	// Check API key first
	apiKey := os.Getenv("RAVE_API_KEY")
	if apiKey != "1234" {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "❌ Invalid API key. Please contact your administrator to get a valid API key for Rave services.",
			}},
			IsError: true,
		}
	}
	
	count := getInt(arguments, "count")
	if count == 0 {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: "❌ Please specify the number of physicians to display. Example: 'create list with 1000 candidates'",
			}},
			IsError: true,
		}
	}
	
	// Prepare API parameters
	params := url.Values{}
	params.Set("points", strconv.Itoa(count))
	params.Set("radius", strconv.Itoa(getIntWithDefault(arguments, "radius", 50)))
	params.Set("clusters", strconv.Itoa(getIntWithDefault(arguments, "clusters", 50)))
	
	// Add API key if provided
	if apiKey := os.Getenv("RAVE_API_KEY"); apiKey != "" {
		params.Set("api_key", apiKey)
	}
	
	if lat, ok := arguments["lat"].(float64); ok {
		params.Set("lat", fmt.Sprintf("%f", lat))
	}
	if lon, ok := arguments["lon"].(float64); ok {
		params.Set("lon", fmt.Sprintf("%f", lon))
	}
	
	// Call the Lambda API
	apiURL := "https://dcujcwokb9.execute-api.us-east-1.amazonaws.com/prod/generate-map"
	fullURL := fmt.Sprintf("%s?%s", apiURL, params.Encode())
	
	fmt.Fprintf(os.Stderr, "Making API call to %s\n", fullURL)
	
	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Get(fullURL)
	if err != nil {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("❌ Network error calling map API: %s", err.Error()),
			}},
			IsError: true,
		}
	}
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("❌ Error reading API response: %s", err.Error()),
			}},
			IsError: true,
		}
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(body, &result); err != nil {
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("❌ Error parsing API response: %s", err.Error()),
			}},
			IsError: true,
		}
	}
	
	if success, ok := result["success"].(bool); ok && success {
		mapURL := getString(result, "url")
		parameters, _ := result["parameters"].(map[string]interface{})
		
		points := getIntWithDefault(parameters, "points", count)
		radiusMiles := getIntWithDefault(parameters, "radius_miles", 50)
		clustersGenerated := getIntWithDefault(parameters, "clusters_generated", 0)
		centerLat := getString(parameters, "center_lat")
		centerLon := getString(parameters, "center_lon")
		
		responseText := fmt.Sprintf(`📍 **Physician Distribution Map Created!**

🔗 **MAP LINK: %s**

**%s Physicians** in a **%d mile radius**

📊 **Map Details:**
• Generated %d clusters  
• Center: %s, %s
• Interactive map with physician concentration visualization

🚨 **IMPORTANT: Click this link to view your map:** %s

The map shows physician distribution with clustering and is ready for analysis.`, 
			mapURL, formatNumber(points), radiusMiles, clustersGenerated, centerLat, centerLon, mapURL)
		
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: responseText,
			}},
		}
	} else {
		errorMsg := getString(result, "error")
		if errorMsg == "" {
			errorMsg = "Unknown error"
		}
		return ToolResult{
			Content: []TextContent{{
				Type: "text",
				Text: fmt.Sprintf("❌ Error creating map: %s", errorMsg),
			}},
			IsError: true,
		}
	}
}

func getString(m map[string]interface{}, key string) string {
	if val, ok := m[key].(string); ok {
		return val
	}
	return ""
}

func getInt(m map[string]interface{}, key string) int {
	if val, ok := m[key].(float64); ok {
		return int(val)
	}
	return 0
}

func getIntWithDefault(m map[string]interface{}, key string, defaultVal int) int {
	if val := getInt(m, key); val != 0 {
		return val
	}
	return defaultVal
}

func formatNumber(n int) string {
	if n >= 1000 {
		return fmt.Sprintf("%d,%d", n/1000, n%1000)
	}
	return strconv.Itoa(n)
}

func sendResponse(id int, result interface{}) {
	response := JsonRpcResponse{
		JsonRpc: "2.0",
		ID:      id,
		Result:  result,
	}
	
	data, _ := json.Marshal(response)
	fmt.Println(string(data))
	os.Stdout.Sync()
}

func sendError(id, code int, message string) {
	response := JsonRpcResponse{
		JsonRpc: "2.0",
		ID:      id,
		Error: &JsonRpcError{
			Code:    code,
			Message: message,
		},
	}
	
	data, _ := json.Marshal(response)
	fmt.Println(string(data))
	os.Stdout.Sync()
}

func runDiagnostics() {
	var messages []string
	var hasErrors bool
	
	messages = append(messages, "🔧 Rave MCP Server - Configuration Diagnostics")
	messages = append(messages, "")
	
	// Check Claude Desktop config path
	configPath := getClaudeConfigPath()
	messages = append(messages, fmt.Sprintf("📁 Config Path: %s", configPath))
	
	// Check if config file exists
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		messages = append(messages, "❌ Claude Desktop config file not found!")
		messages = append(messages, fmt.Sprintf("   Please create: %s", configPath))
		messages = append(messages, "")
		messages = append(messages, "📝 Sample Configuration needed:")
		currentBinary, _ := os.Executable()
		messages = append(messages, `{
  "mcpServers": {
    "rave": {
      "command": "`+currentBinary+`",
      "args": [],
      "env": {
        "RAVE_API_KEY": "1234"
      }
    }
  }
}`)
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, "✅ Config file exists")
	
	// Read and validate JSON
	configData, err := os.ReadFile(configPath)
	if err != nil {
		messages = append(messages, fmt.Sprintf("❌ Error reading config file: %s", err))
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	var config map[string]interface{}
	if err := json.Unmarshal(configData, &config); err != nil {
		messages = append(messages, "❌ Invalid JSON in config file!")
		messages = append(messages, fmt.Sprintf("   JSON Error: %s", err))
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, "✅ Config file has valid JSON")
	
	// Check for mcpServers section
	mcpServers, ok := config["mcpServers"].(map[string]interface{})
	if !ok {
		messages = append(messages, "❌ No 'mcpServers' section found in config")
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, "✅ mcpServers section found")
	
	// Check for rave server
	raveServer, ok := mcpServers["rave"].(map[string]interface{})
	if !ok {
		messages = append(messages, "❌ No 'rave' server configured in mcpServers")
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, "✅ Rave server configured")
	
	// Check command path
	command, ok := raveServer["command"].(string)
	if !ok {
		messages = append(messages, "❌ No 'command' specified for rave server")
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, fmt.Sprintf("📍 Command path: %s", command))
	
	// Check if binary exists
	if _, err := os.Stat(command); os.IsNotExist(err) {
		messages = append(messages, "❌ Rave MCP binary not found!")
		messages = append(messages, fmt.Sprintf("   Expected at: %s", command))
		hasErrors = true
		showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
		return
	}
	
	messages = append(messages, "✅ Rave MCP binary exists")
	
	// Check API key
	if env, ok := raveServer["env"].(map[string]interface{}); ok {
		if apiKey, ok := env["RAVE_API_KEY"].(string); ok {
			if apiKey == "1234" {
				messages = append(messages, "✅ API key configured correctly")
			} else if apiKey == "your-api-key-here" {
				messages = append(messages, "⚠️  API key is placeholder - update to '1234' for testing")
				hasErrors = true
			} else {
				messages = append(messages, fmt.Sprintf("⚠️  API key is set to: %s (expected: 1234 for testing)", apiKey))
				hasErrors = true
			}
		} else {
			messages = append(messages, "❌ No RAVE_API_KEY found in environment variables")
			messages = append(messages, "")
			messages = append(messages, "📝 Add this to your rave server config:")
			messages = append(messages, `"env": {
  "RAVE_API_KEY": "1234"
}`)
			hasErrors = true
		}
	} else {
		messages = append(messages, "❌ No environment variables configured")
		messages = append(messages, "")
		messages = append(messages, "📝 Add this to your rave server config:")
		messages = append(messages, `"env": {
  "RAVE_API_KEY": "1234"
}`)
		hasErrors = true
	}
	
	messages = append(messages, "")
	if hasErrors {
		messages = append(messages, "⚠️  Please fix the issues above and restart Claude Desktop")
	} else {
		messages = append(messages, "🎉 Configuration validation complete!")
		messages = append(messages, "   Restart Claude Desktop if you made any changes.")
	}
	
	showPopup("Rave MCP Diagnostics", strings.Join(messages, "\n"), hasErrors)
}

func getClaudeConfigPath() string {
	switch runtime.GOOS {
	case "darwin": // macOS
		home, _ := os.UserHomeDir()
		return filepath.Join(home, "Library", "Application Support", "Claude", "claude_desktop_config.json")
	case "windows":
		appData := os.Getenv("APPDATA")
		return filepath.Join(appData, "Claude", "claude_desktop_config.json")
	default:
		// Linux fallback
		home, _ := os.UserHomeDir()
		return filepath.Join(home, ".config", "Claude", "claude_desktop_config.json")
	}
}

func showSampleConfig() {
	currentBinary, _ := os.Executable()
	
	fmt.Println("📝 Sample Configuration:")
	fmt.Printf(`{
  "mcpServers": {
    "rave": {
      "command": "%s",
      "args": [],
      "env": {
        "RAVE_API_KEY": "1234"
      }
    }
  }
}`, currentBinary)
	fmt.Println()
}

func showApiKeyConfig() {
	fmt.Println()
	fmt.Println("📝 Add this to your rave server config:")
	fmt.Println(`"env": {
  "RAVE_API_KEY": "1234"
}`)
}

func showPopup(title, message string, isError bool) {
	switch runtime.GOOS {
	case "darwin": // macOS
		// Use osascript to show dialog
		iconType := "note"
		if isError {
			iconType = "caution"
		}
		
		cmd := exec.Command("osascript", "-e", fmt.Sprintf(`display dialog "%s" with title "%s" with icon %s buttons {"OK"} default button "OK"`, 
			strings.ReplaceAll(message, `"`, `\"`), 
			title, 
			iconType))
		cmd.Run()
		
	case "windows":
		// Use PowerShell to show message box
		iconType := "Information"
		if isError {
			iconType = "Warning"
		}
		
		psScript := fmt.Sprintf(`Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('%s', '%s', 'OK', '%s')`, 
			strings.ReplaceAll(message, `'`, `''`), 
			title, 
			iconType)
		
		cmd := exec.Command("powershell", "-Command", psScript)
		cmd.Run()
		
	default:
		// Fallback to console output for Linux
		fmt.Printf("=== %s ===\n", title)
		fmt.Println(message)
		fmt.Println("\nPress Enter to continue...")
		bufio.NewReader(os.Stdin).ReadLine()
	}
}