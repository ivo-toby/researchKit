---
description: Synthesize research findings into a comprehensive report
tags: [researchkit, synthesize, report]
---

# ResearchKit: Synthesize

You are helping to synthesize research findings into a comprehensive, well-cited report.

## Your Task

1. **Verify Execution is Complete**

   Check that research files exist and are populated:
   ```bash
   bash .researchkit/scripts/bash/synthesize.sh
   ```

   This creates synthesis.md from template

2. **Review All Research Materials**

   Read thoroughly:
   - plan.md - Original research question and objectives
   - findings.md - All documented findings and notes
   - sources.md - Complete bibliography

3. **Create the Synthesis**

   Edit synthesis.md with:

   **Executive Summary**
   - 2-3 paragraph overview
   - Key findings highlighted
   - Main conclusions stated

   **Research Question Recap**
   - Restate the original question
   - Provide context

   **Methodology Summary**
   - How research was conducted
   - Sources consulted (with counts)
   - Time period covered

   **Key Findings** (Most Important!)
   - Each major finding gets its own section
   - State finding clearly
   - Provide evidence from 3+ sources
   - Include proper citations
   - Rate confidence level (High/Medium/Low)
   - Explain implications

   **Analysis & Discussion**
   - Synthesize patterns across findings
   - Connect the dots between sources
   - Address conflicting viewpoints
   - Discuss limitations

   **Conclusions**
   - Direct answer to research question
   - Key takeaways (3-5 bullet points)
   - Confidence assessment with reasoning

   **Recommendations**
   - Actionable recommendations based on findings
   - Areas for further research
   - Update schedule if topic evolves

   **Bibliography**
   - Complete, properly formatted
   - Alphabetically ordered
   - Consistent format

## Quality Standards

**Every Claim Must Be Cited**
- If you state a fact, include citation
- Use multiple citations for important claims
- Format: (Author, Year) or [1] based on constitution

**Evidence-Based Conclusions**
- Conclusions must follow from evidence
- Don't overstate confidence
- Acknowledge limitations
- Note gaps in research

**Clear Structure**
- Logical flow from question to answer
- Each section serves a purpose
- Easy to navigate
- Key points highlighted

**Professional Tone**
- Objective and balanced
- Acknowledges uncertainty
- Clear and concise
- No unsupported opinions

## Synthesis Checklist

Run through before finalizing:

- [ ] Research question clearly answered
- [ ] All major findings documented with evidence
- [ ] Every claim properly cited
- [ ] Conflicting information addressed
- [ ] Limitations acknowledged
- [ ] Source quality evaluated
- [ ] Bibliography complete and formatted
- [ ] Confidence levels justified
- [ ] Implications explained
- [ ] Recommendations actionable
- [ ] Writing is clear and professional

## Handle Edge Cases

**If research was incomplete**:
- Document what WAS found
- Explain gaps and why
- Recommend next steps
- Note as partial/preliminary

**If findings conflict**:
- Present all viewpoints
- Evaluate quality of each source
- Explain which has stronger support
- Acknowledge uncertainty if unresolved

**If question can't be answered**:
- Explain why (lack of sources, scope too broad, etc.)
- Summarize what IS known
- Suggest how to make progress

## Finalize

Once synthesis.md is complete:

1. **Review Against Constitution**
   - Meets all quality standards
   - Follows citation requirements
   - Proper verification conducted

2. **Commit the Synthesis**
   ```bash
   git add .researchkit/research/*
   git commit -m "research: Complete synthesis for [topic]

   Final research report with [N] sources analyzed.
   Key findings: [brief summary]
   Confidence: [High/Medium/Low]"
   ```

3. **Optional: Create Pull Request**
   If this research should be reviewed:
   ```bash
   git push -u origin research/NNN-topic-name
   # Then create PR in GitHub
   ```

## Example Citation Formats

**APA**:
- In-text: (Smith, 2023, p. 42)
- Bibliography: Smith, J. (2023). *Title*. Publisher.

**IEEE**:
- In-text: [1]
- Bibliography: [1] J. Smith, "Title," Publication, 2023.

Use the format specified in your constitution!

---

Remember: A good synthesis is like a story - it takes the reader from question to answer with clear evidence at every step.
