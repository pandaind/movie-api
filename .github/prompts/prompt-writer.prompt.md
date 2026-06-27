---
name: "write-prompt"
description: "Generate a new slash command shortcut"
agent: "forge-prompt-writer"
argument-hint: "[slash command purpose]"
---

Please generate a new slash command configuration based on the following requirements:
${input:requirements:What should this slash command do?}

Ensure you include the required YAML frontmatter and save it to `.github/prompts/`.
