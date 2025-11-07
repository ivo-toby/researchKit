#!/usr/bin/env bash
# ResearchKit Plan Script - Create a research plan

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

show_header "Research Planning Phase"

# Parse arguments
RESEARCH_TOPIC="$1"

if [ -z "$RESEARCH_TOPIC" ]; then
    print_error "Research topic is required"
    echo "Usage: $0 <research-topic>" >&2
    echo "Example: $0 \"AI Safety Research\"" >&2
    exit 1
fi

# Check prerequisites
check_git_initialized

# Create research project
print_step "Creating research project..."
RESEARCH_DIR=$(create_research_project "$RESEARCH_TOPIC")
RESEARCH_NAME=$(basename "$RESEARCH_DIR")

# Create plan.md from template
print_step "Setting up research plan..."
PLAN_FILE="${RESEARCH_DIR}/plan.md"

if check_file_exists "$PLAN_FILE"; then
    print_info "Updating existing plan"
fi

copy_template "plan-template.md" "$PLAN_FILE"

# Update placeholders in plan.md
update_date_in_file "$PLAN_FILE"

# Replace research topic placeholder
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$PLAN_FILE"
    sed -i '' "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$PLAN_FILE"
else
    sed -i "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$PLAN_FILE"
    sed -i "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$PLAN_FILE"
fi

# Create sources.md
print_step "Creating sources file..."
SOURCES_FILE="${RESEARCH_DIR}/sources.md"
cat > "$SOURCES_FILE" << EOF
# Research Sources: ${RESEARCH_TOPIC}

**Research ID**: ${RESEARCH_NAME}
**Created**: $(date +%Y-%m-%d)

---

## Bibliography

Sources will be added here as research progresses.

### Format
Use consistent citation format (APA recommended):

**Example**:
Author, A. (Year). Title of work. *Publication*. URL

---

## Source Tracking

| # | Author | Title | Type | Date | Quality | Status |
|---|--------|-------|------|------|---------|--------|
| 1 | | | | | ⭐⭐⭐ | 📝 Reading |

**Quality Scale**: ⭐ (Low) to ⭐⭐⭐⭐⭐ (Peer-reviewed)
**Status Icons**: 📝 Reading | ✅ Completed | 📌 Key Source

---

## Notes

Add notes about source discovery, search strategies, etc.
EOF

print_success "Created sources tracking file"

# Create initial commit
print_step "Committing research plan..."
git add "$RESEARCH_DIR"
git commit -m "$(cat <<EOF
research: Initialize ${RESEARCH_TOPIC}

Create research project ${RESEARCH_NAME} with plan template.

Research structure:
- Plan: Define research questions and strategy
- Sources: Track bibliography and citations
- Ready for execution phase
EOF
)" 2>/dev/null || print_warning "Nothing new to commit"

# Display summary
echo "" >&2
print_success "Research plan created successfully!"
echo "" >&2
print_info "Research Project: ${RESEARCH_NAME}"
print_info "Branch: research/${RESEARCH_NAME}"
print_info "Directory: ${RESEARCH_DIR}"
echo "" >&2
echo -e "${CYAN}Next steps:${NC}" >&2
echo "  1. Edit ${PLAN_FILE}" >&2
echo "  2. Define your research question and objectives" >&2
echo "  3. Set up your search strategy" >&2
echo "  4. Use /researchkit.execute to begin research" >&2
echo "" >&2
