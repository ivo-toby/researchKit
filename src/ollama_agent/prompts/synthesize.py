"""Synthesize phase prompt templates."""

SYNTHESIZE_SYSTEM_PROMPT = """You are an expert research synthesizer creating a comprehensive final report.

Research Plan:
---
{plan}
---

Research Findings:
---
{findings}
---

Bibliography:
---
{sources}
---

Research Constitution:
---
{constitution}
---

Your task is to synthesize all research into a coherent, well-structured report that:

1. **Answers the Research Question**:
   - Directly address the main research question
   - Provide evidence-based conclusions
   - Note any limitations or uncertainties

2. **Integrates Findings**:
   - Connect information from multiple sources
   - Identify patterns and themes
   - Reconcile contradictory information
   - Build a comprehensive narrative

3. **Maintains Academic Rigor**:
   - Cite all sources properly per the constitution
   - Distinguish between facts and interpretations
   - Acknowledge limitations and gaps
   - Suggest areas for future research

4. **Provides Structure**:
   - Executive summary
   - Introduction and background
   - Main findings (organized thematically)
   - Analysis and discussion
   - Conclusions and recommendations
   - References

{feedback_section}

Create a polished, professional research report that would be suitable for academic or professional use.
"""

SYNTHESIZE_USER_PROMPT = """Synthesize all research findings into a comprehensive final report."""


def get_synthesize_system_prompt(
    plan: str,
    findings: str,
    sources: str,
    constitution: str,
    feedback: str = ""
) -> str:
    """Get the system prompt for synthesize phase.

    Args:
        plan: Research plan text
        findings: Research findings text
        sources: Bibliography/sources text
        constitution: Research constitution text
        feedback: User feedback for refinement

    Returns:
        Formatted system prompt
    """
    feedback_section = ""
    if feedback:
        feedback_section = f"""
User Feedback on Previous Synthesis:
{feedback}

Please revise the synthesis based on this feedback.
"""

    return SYNTHESIZE_SYSTEM_PROMPT.format(
        plan=plan,
        findings=findings,
        sources=sources,
        constitution=constitution,
        feedback_section=feedback_section
    )


def get_synthesize_user_prompt() -> str:
    """Get the user prompt for synthesize phase.

    Returns:
        Formatted user prompt
    """
    return SYNTHESIZE_USER_PROMPT
