---
description: Manage and verify research sources and bibliography
tags: [researchkit, sources, bibliography]
---

# ResearchKit: Sources

You are helping to manage research sources and maintain a proper bibliography.

## Your Task

Help the user manage their research sources with proper citation practices.

## Commands

### View Current Sources

```bash
cat .researchkit/research/*/sources.md
```

### Add a Source

When the user provides a source, add it to sources.md with:

1. **Full Citation** (format per constitution)
   - Author(s)
   - Publication year
   - Title
   - Publication/Journal
   - DOI or URL
   - Access date (for web sources)

2. **Source Metadata**
   - Type (peer-reviewed, technical doc, blog, etc.)
   - Quality rating (⭐ to ⭐⭐⭐⭐⭐)
   - Relevance (High/Medium/Low)
   - Status (Reading/Completed/Key Source)

3. **Quick Notes**
   - What this source covers
   - Why it's relevant
   - Any limitations

### Verify Citations

Check that:
- All sources in findings.md are in sources.md
- All citations are properly formatted
- URLs are accessible
- Dates are included
- No duplicate entries

Run a verification:
```bash
# Check for citation markers in findings
grep -o '\[.*\]' .researchkit/research/*/findings.md | sort -u

# Compare with sources list
grep -E '^\d+\.' .researchkit/research/*/sources.md
```

### Export Bibliography

Create a standalone bibliography file:

```bash
# Extract bibliography section from sources.md
cat .researchkit/research/*/sources.md | \
  sed -n '/## Bibliography/,$p' > bibliography.txt
```

## Source Quality Evaluation

Help users evaluate source quality using these criteria:

### ⭐⭐⭐⭐⭐ Excellent
- Peer-reviewed academic journals
- Official technical documentation
- Government research reports
- Well-established references

### ⭐⭐⭐⭐ High Quality
- Industry research reports
- Expert analysis from credentialed authors
- Technical blog posts from recognized experts
- Reputable news organizations

### ⭐⭐⭐ Medium Quality
- General technical blogs
- Company blog posts
- Trade publications
- Well-sourced journalism

### ⭐⭐ Lower Quality
- Personal blogs
- Social media from experts
- Forums (Stack Overflow, Reddit)
- Marketing materials

### ⭐ Use with Caution
- Anonymous sources
- Uncited claims
- Extreme bias
- Social media from non-experts

## Common Citation Formats

### APA (American Psychological Association)
```
Author, A. A. (Year). Title of work. Publication. https://doi.org/xxx

Example:
Smith, J., & Jones, M. (2023). Modern authentication patterns.
  Journal of Web Security, 15(3), 234-256. https://doi.org/10.1234/jws.2023.123
```

### IEEE
```
[#] A. A. Author, "Title of paper," Journal, vol. X, no. Y, pp. ZZ-ZZ, Month Year.

Example:
[1] J. Smith and M. Jones, "Modern authentication patterns,"
    Journal of Web Security, vol. 15, no. 3, pp. 234-256, June 2023.
```

### Chicago
```
Author, First. "Title of Article." Journal Name Vol, no. Issue (Year): pages.

Example:
Smith, John, and Mary Jones. "Modern Authentication Patterns."
  Journal of Web Security 15, no. 3 (2023): 234-256.
```

## Managing Sources

### Add Source Interactively

When user says "add this source" and provides details:

1. Extract metadata
2. Format citation
3. Add to sources.md
4. Assign quality rating
5. Note relevance

### Find Missing Citations

```bash
# Find uncited claims in findings
# (Claims without immediate citation)
grep -n '[.!]$' .researchkit/research/*/findings.md | \
  grep -v '\[.*\]' | head -20
```

### Check for Dead Links

```bash
# Extract all URLs
grep -oP 'https?://[^\s]+' .researchkit/research/*/sources.md
```

Then verify each is accessible

### Update Source Status

As research progresses, update status in the source tracking table:
- 📝 Reading → ✅ Completed
- Mark key sources: 📌

## Source Management Tips

**Cite as You Go**: Don't wait until synthesis - add sources immediately

**Be Consistent**: Use one citation format throughout (check constitution)

**Include Access Dates**: For web sources, note when you accessed them

**Check Links**: Verify URLs work before finalizing

**Rate Quality**: Helps during synthesis to weight evidence

**Note Limitations**: Document if source is outdated, biased, or limited

**Track Versions**: For technical docs, note version numbers

**Keep Metadata**: Full citation details now saves time later

## Commit Source Updates

```bash
git add .researchkit/research/*/sources.md
git commit -m "research: Update bibliography with [N] new sources"
```

## Export Formats

Help users export their bibliography in different formats:

**Plain Text**: Copy from sources.md

**BibTeX**: For LaTeX users
```bibtex
@article{smith2023modern,
  author = {Smith, John and Jones, Mary},
  title = {Modern Authentication Patterns},
  journal = {Journal of Web Security},
  year = {2023},
  volume = {15},
  number = {3},
  pages = {234--256}
}
```

**RIS**: For reference managers
```ris
TY  - JOUR
AU  - Smith, John
AU  - Jones, Mary
TI  - Modern Authentication Patterns
JO  - Journal of Web Security
PY  - 2023
VL  - 15
IS  - 3
SP  - 234
EP  - 256
ER  -
```

Remember: Good source management makes synthesis much easier!
