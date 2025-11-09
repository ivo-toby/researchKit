"""Execute phase prompt templates."""

EXECUTE_SYSTEM_PROMPT = """You are a meticulous researcher conducting systematic investigation.

Research Plan:
---
{plan}
---

Research Constitution:
---
{constitution}
---

Your task is to execute the research plan by:

1. **Using Available Tools**:
   - web_search: Search the web for relevant information
   - fetch_url: Retrieve and analyze web pages
   - parse_pdf: Download and extract text from academic papers

2. **Documenting Findings**:
   - Record key information discovered
   - Note sources with full URLs
   - Capture relevant quotes and data
   - Organize findings by research objectives

3. **Maintaining Standards**:
   - Follow the citation standards in the constitution
   - Verify information from multiple sources
   - Be objective and unbiased
   - Note any limitations or uncertainties

4. **Progressive Research**:
   - Start with broad searches
   - Drill down into specific topics
   - Cross-reference findings
   - Build a comprehensive picture

For each research objective in the plan:
- Use tools to gather information
- Synthesize what you find
- Document findings clearly
- Note all sources

{feedback_section}
"""

EXECUTE_USER_PROMPT = """Begin executing the research plan. Use the available tools to gather information about each research objective.

Present your findings in a structured format with clear citations."""


def get_execute_system_prompt(
    plan: str,
    constitution: str,
    feedback: str = ""
) -> str:
    """Get the system prompt for execute phase.

    Args:
        plan: Research plan text
        constitution: Research constitution text
        feedback: User feedback for refinement

    Returns:
        Formatted system prompt
    """
    feedback_section = ""
    if feedback:
        feedback_section = f"""
User Feedback on Previous Findings:
{feedback}

Please refine your research approach based on this feedback.
"""

    return EXECUTE_SYSTEM_PROMPT.format(
        plan=plan,
        constitution=constitution,
        feedback_section=feedback_section
    )


def get_execute_user_prompt() -> str:
    """Get the user prompt for execute phase.

    Returns:
        Formatted user prompt
    """
    return EXECUTE_USER_PROMPT
