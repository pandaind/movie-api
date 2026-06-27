---
name: "write-workflow"
description: "Generate a GitHub Actions automated workflow"
agent: "forge-workflow-writer"
argument-hint: "[workflow purpose and triggers]"
---

Please generate a new GitHub Actions workflow based on the following requirements:
${input:requirements:What should this workflow automate?}

Ensure it is valid YAML syntax for GitHub Actions and saved to `.github/workflows/`.
