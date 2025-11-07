---
description: Define or update research methodology principles and standards
tags: [researchkit, setup, methodology]
---

# ResearchKit: Constitution

You are helping to define or update the research constitution for this project.

## Current Constitution

Read the current constitution:
```bash
cat .researchkit/memory/constitution.md
```

## Your Task

Help the user define or refine their research methodology principles:

1. **Citation Standards**
   - What citation format to use (APA, MLA, Chicago, etc.)
   - When citations are required
   - How to handle different source types

2. **Source Quality Standards**
   - How to evaluate source credibility
   - Preferred source types (peer-reviewed, technical docs, etc.)
   - Red flags to watch for
   - Quality rating system

3. **Research Process Structure**
   - How to approach the planning phase
   - Documentation requirements during execution
   - Synthesis and analysis approach
   - Review and quality assurance

4. **Verification Requirements**
   - How many sources needed to verify claims
   - Cross-referencing standards
   - Handling conflicting information
   - Fact-checking procedures

## Guidelines

- Ask clarifying questions if the user's requirements are ambiguous
- Provide sensible defaults based on best practices
- Tailor the constitution to their specific research domain
- Make it actionable and specific, not just aspirational
- Consider their typical research topics and needs

## Output

Once you understand their requirements, update `.researchkit/memory/constitution.md` with:
- Clear, specific standards
- Practical guidelines they can follow
- Examples where helpful
- Checklists for quality assurance

The constitution should be a **living document** that guides all research in this project.

## Example Scenarios

**Academic Research**: Emphasize peer-reviewed sources, formal citations, rigorous verification

**Technical Research**: Focus on official documentation, version-specific information, reproducibility

**Market Research**: Include industry reports, expert analysis, data source verification

**General Knowledge**: Balance accessibility with quality, multiple source verification

After updating the constitution, commit the changes:
```bash
git add .researchkit/memory/constitution.md
git commit -m "research: Update research constitution"
```
