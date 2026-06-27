---
name: "write-mcp"
description: "Generate a Model Context Protocol (MCP) integration"
agent: "forge-mcp-writer"
argument-hint: "[MCP server integration details]"
---

Please generate a new MCP server configuration based on the following requirements:
${input:requirements:What external tool should this connect to?}

Format it as valid JSON to be placed in `.vscode/mcp.json`.
