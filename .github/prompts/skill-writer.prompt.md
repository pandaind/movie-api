---
name: "write-skill"
description: "Generate a new skill or knowledge pack"
agent: "forge-skill-writer"
argument-hint: "[domain knowledge to document]"
---

Please generate a new `SKILL.md` knowledge pack based on the following requirements:
${input:requirements:What domain knowledge should this skill cover?}

Create a new directory for it in `.github/skills/` and save the `SKILL.md` file there.
