---
name: "write-instruction"
description: "Generate a new ruleset for specific file patterns"
agent: "forge-instruction-writer"
argument-hint: "[file pattern] [rules]"
---

Please generate a new instruction set based on the following requirements:
${input:requirements:What rules do you want to enforce and on what files?}

Ensure you include YAML frontmatter with file targeting (`patterns: [...]`) and save it to `.github/instructions/`.
