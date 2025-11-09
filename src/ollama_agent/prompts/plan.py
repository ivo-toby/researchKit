"""Plan phase prompt templates."""

PLAN_SYSTEM_PROMPT = """You are a research planning expert. Create a detailed, actionable research plan.

Your plan should include:

1. **Research Question**: A clear, focused question to investigate
2. **Objectives**: 3-5 specific, measurable goals
3. **Methodology**: Detailed approach for conducting the research
4. **Key Topics**: Main areas and subtopics to investigate
5. **Success Criteria**: How to determine when research is complete

Use the following template structure:
---
{template}
---

Adhere to the research constitution:
---
{constitution}
---

{feedback_section}

The plan should be:
- Specific and actionable
- Realistic in scope
- Well-organized and structured
- Aligned with the constitution's principles
"""

PLAN_USER_PROMPT = """Research Topic: {topic}

Please create a comprehensive research plan for investigating this topic."""


def get_plan_system_prompt(
    constitution: str,
    template: str,
    feedback: str = ""
) -> str:
    """Get the system prompt for plan phase.

    Args:
        constitution: Research constitution text
        template: Plan template structure
        feedback: User feedback for refinement

    Returns:
        Formatted system prompt
    """
    feedback_section = ""
    if feedback:
        feedback_section = f"""
User Feedback on Previous Plan:
{feedback}

Please incorporate this feedback into the revised plan.
"""

    return PLAN_SYSTEM_PROMPT.format(
        template=template,
        constitution=constitution,
        feedback_section=feedback_section
    )


def get_plan_user_prompt(topic: str) -> str:
    """Get the user prompt for plan phase.

    Args:
        topic: Research topic

    Returns:
        Formatted user prompt
    """
    return PLAN_USER_PROMPT.format(topic=topic)
