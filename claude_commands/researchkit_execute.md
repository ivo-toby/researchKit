---
description: Execute research plan with structured documentation
tags: [researchkit, execute, research]
---

# ResearchKit: Execute

You are helping to execute a research plan with proper documentation and citation practices.

## Your Task

1. **Initialize Execution**

   Run the execution script:
   ```bash
   bash .researchkit/scripts/bash/execute.sh
   ```

   This verifies you're on a research branch and sets up findings.md

2. **Review the Research Plan**

   Read the plan to understand:
   - Research question
   - Objectives
   - Search strategy
   - Success criteria

   ```bash
   cat .researchkit/research/*/plan.md
   ```

3. **Execute Research Systematically**

   Follow the plan's phases:

   **Phase 1: Broad Exploration**
   - Use web search for initial information gathering
   - Cast a wide net with various keywords
   - Document EVERY source immediately in sources.md
   - Take structured notes in findings.md
   - Format: Session log with date, focus, findings

   **Phase 2: Deep Investigation**
   - Focus on specific areas identified in Phase 1
   - Seek authoritative, high-quality sources
   - Cross-reference claims
   - Note emerging themes and patterns
   - Continue documenting in findings.md

   **Phase 3: Cross-Verification**
   - Verify key claims with multiple sources
   - Check for conflicting information
   - Evaluate source quality
   - Note confidence levels
   - Prepare for synthesis

4. **Documentation Standards**

   **In findings.md**:
   - Use chronological session structure
   - For each source, document:
     * Full citation details
     * Relevance rating (High/Medium/Low)
     * Key points extracted
     * Direct quotes with page numbers
     * Your analysis and connections
   - Note emerging themes
   - Document questions that arise
   - Mark gaps and limitations

   **In sources.md**:
   - Maintain complete bibliography
   - Use consistent citation format (per constitution)
   - Track source quality ratings
   - Add URLs and access dates

5. **Follow the Constitution**

   Check `.researchkit/memory/constitution.md` for:
   - Citation requirements
   - Source quality standards
   - Verification requirements
   - Documentation practices

## Research Best Practices

**Always Cite Immediately**: Don't wait - add sources as you find them

**Evaluate Sources**: Check author credentials, publication date, potential bias

**Note Confidence**: Mark claims as high/medium/low confidence based on evidence

**Document Process**: Future you will thank present you for good notes

**Track Questions**: Research often generates new questions - write them down

**Commit Regularly**: Save your progress with git commits

## Using Web Search Effectively

- Start broad, then narrow based on what you find
- Use multiple search queries to avoid bias
- Check multiple sources for important claims
- Look for primary sources when possible
- Note when information is outdated
- Use quote marks for exact phrase matching
- Use site: operator for specific sources (site:arxiv.org)

## Red Flags

Watch out for:
- Uncited claims
- Missing author/date information
- Extreme bias or agenda
- Conflicts with multiple reliable sources
- Behind paywall without access
- Broken links or unavailable sources

## Commit Your Work

Regularly commit research progress:
```bash
git add .researchkit/research/*
git commit -m "research: Document findings from [topic/phase]"
```

## When Complete

Once you've:
- Answered the research question (or documented why you can't)
- Gathered sufficient evidence
- Documented all sources
- Verified key claims

Then: Use `/researchkit.synthesize` to generate the final report

Remember: Good research is about **quality** over quantity. Better to have 5 excellent sources than 50 mediocre ones!
