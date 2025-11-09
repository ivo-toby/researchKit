"""Constitution phase prompt templates."""

CONSTITUTION_SYSTEM_PROMPT = """You are a research methodology expert helping to define clear research principles.

Your role is to help create or refine a research constitution that includes:

1. **Citation Standards**: How sources should be cited (e.g., APA, MLA, Chicago)
2. **Source Quality Requirements**: What makes a credible source (peer-reviewed, primary sources, etc.)
3. **Verification Procedures**: How to fact-check and cross-reference information
4. **Research Ethics**: How to handle bias, ensure diverse perspectives, maintain objectivity

The constitution should be:
- Concise (1-2 pages maximum)
- Clear and actionable
- Tailored to the research domain
- Comprehensive but not overwhelming

{current_constitution_section}

If the user provides feedback, incorporate it thoughtfully and revise the constitution accordingly.
"""

CONSTITUTION_USER_PROMPT = """Help me {action} a research constitution for this project.

{feedback_section}

Please provide a well-structured research constitution that defines the methodological principles for conducting research."""


def get_constitution_system_prompt(current_constitution: str = "") -> str:
    """Get the system prompt for constitution phase.

    Args:
        current_constitution: Existing constitution text, if any

    Returns:
        Formatted system prompt
    """
    if current_constitution:
        current_section = f"""
Current Constitution:
---
{current_constitution}
---

Please review the current constitution and suggest improvements or refinements.
"""
    else:
        current_section = "There is no existing constitution. Please create one from scratch."

    return CONSTITUTION_SYSTEM_PROMPT.format(
        current_constitution_section=current_section
    )


def get_constitution_user_prompt(feedback: str = "") -> str:
    """Get the user prompt for constitution phase.

    Args:
        feedback: User feedback for refinement

    Returns:
        Formatted user prompt
    """
    action = "refine" if feedback else "create"

    feedback_section = ""
    if feedback:
        feedback_section = f"""
User Feedback:
{feedback}

Please incorporate this feedback into the constitution.
"""

    return CONSTITUTION_USER_PROMPT.format(
        action=action,
        feedback_section=feedback_section
    )
