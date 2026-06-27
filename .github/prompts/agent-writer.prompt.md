---
name: "write-agent"
description: "Generate a new AI agent persona"
agent: "forge-agent-writer"
argument-hint: "[agent role and responsibilities]"
---

Please generate a new Agent persona based on the following requirements:
${input:requirements:What kind of agent do you want to create?}

Ensure the new agent follows the standard Agent Forge format and save it to `.github/agents/`.
