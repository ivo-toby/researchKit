---
description: Create a structured research plan for a new research project
tags: [researchkit, plan, start]
---

# ResearchKit: Plan

You are helping to create a structured research plan.

## Your Task

1. **Understand the Research Question**
   - Ask the user what they want to research
   - Help them refine a vague idea into a clear research question
   - Ensure the question is specific and answerable

2. **Define Scope**
   - What's IN scope: Topics, time periods, types of sources
   - What's OUT of scope: Areas explicitly excluded
   - Why these boundaries matter

3. **Create the Research Plan**

   Run the planning script:
   ```bash
   bash .researchkit/scripts/bash/plan.sh "Research Topic Name"
   ```

   This will:
   - Create a new research project with auto-incrementing ID
   - Generate a git branch (research/NNN-topic-name)
   - Create plan.md from template
   - Set up sources.md for bibliography tracking

4. **Customize the Plan**

   Edit the generated plan.md to include:

   **Research Question**: Clear, specific question

   **Objectives**: What you want to achieve (measurable)

   **Search Strategy**:
   - Phase 1: Broad exploration keywords and sources
   - Phase 2: Deep investigation focus areas
   - Phase 3: Cross-verification approach

   **Success Criteria**: How you'll know when you're done

   **Timeline**: Realistic timeline for each phase

5. **Review Against Constitution**
   - Ensure the plan aligns with research methodology principles
   - Check that verification requirements are addressed
   - Confirm citation standards are clear

## Example Research Questions

**Good** ✓:
- "How should we implement authentication in our React app using modern best practices?"
- "What are the key differences between PostgreSQL and MongoDB for our use case?"
- "What evidence exists for the effectiveness of spaced repetition in learning?"

**Too Vague** ✗:
- "Learn about AI" → Refine to: "What are the main architectural patterns in modern LLMs?"
- "Database research" → Refine to: "Which database best fits a high-write, time-series workload?"

## Questions to Ask

If the research topic is unclear, ask:
- What specific question do you want answered?
- What will you do with this information?
- What scope boundaries should we set?
- What sources are most relevant?
- What's your timeline?

## Output

Once the plan is ready:
1. The script will create the structure
2. Help the user fill in the plan.md details
3. Commit the plan with a clear message
4. Inform them they can start execution with `/researchkit.execute`

Remember: A good plan saves time during execution!
