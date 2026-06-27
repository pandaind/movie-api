---
name: "write-hook"
description: "Generate an automation hook configuration"
agent: "forge-hook-writer"
argument-hint: "[hook trigger and script logic]"
---

Please generate a new JSON hook automation based on the following requirements:
${input:requirements:What should this hook do and when should it trigger?}

Ensure it is valid JSON and saved to `.github/hooks/`.
