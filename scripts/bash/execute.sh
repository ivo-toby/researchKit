#!/usr/bin/env bash
# ResearchKit Execute Script - Execute research plan

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

show_header "Research Execution Phase"

# Check prerequisites
check_git_initialized

# Get current research directory
print_step "Loading research project..."
RESEARCH_DIR=$(get_current_research_dir)
RESEARCH_NAME=$(basename "$RESEARCH_DIR")

print_info "Research Project: ${RESEARCH_NAME}"
print_info "Directory: ${RESEARCH_DIR}"
echo "" >&2

# Check if plan exists
PLAN_FILE="${RESEARCH_DIR}/plan.md"
if [ ! -f "$PLAN_FILE" ]; then
    print_error "No research plan found"
    print_info "Create a plan first with /researchkit.plan"
    exit 1
fi

print_success "Research plan found"

# Create findings.md if it doesn't exist
FINDINGS_FILE="${RESEARCH_DIR}/findings.md"
if ! check_file_exists "$FINDINGS_FILE"; then
    print_step "Creating research findings file..."
    copy_template "execution-template.md" "$FINDINGS_FILE"
    update_date_in_file "$FINDINGS_FILE"

    # Extract research topic from plan
    RESEARCH_TOPIC=$(grep -m 1 "^# Research Plan:" "$PLAN_FILE" | sed 's/# Research Plan: //')

    # Update placeholders
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$FINDINGS_FILE"
        sed -i '' "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$FINDINGS_FILE"
    else
        sed -i "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$FINDINGS_FILE"
        sed -i "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$FINDINGS_FILE"
    fi
fi

# Verify sources.md exists
SOURCES_FILE="${RESEARCH_DIR}/sources.md"
if [ ! -f "$SOURCES_FILE" ]; then
    print_warning "Sources file not found, creating it..."
    RESEARCH_TOPIC=$(grep -m 1 "^# Research Plan:" "$PLAN_FILE" | sed 's/# Research Plan: //')
    cat > "$SOURCES_FILE" << EOF
# Research Sources: ${RESEARCH_TOPIC}

**Research ID**: ${RESEARCH_NAME}
**Created**: $(date +%Y-%m-%d)

---

## Bibliography

Sources will be added here as research progresses.

EOF
    print_success "Created sources file"
fi

echo "" >&2
print_success "Research execution environment ready!"
echo "" >&2
echo -e "${CYAN}Research Files:${NC}" >&2
echo "  📋 Plan:     ${PLAN_FILE}" >&2
echo "  📝 Findings: ${FINDINGS_FILE}" >&2
echo "  📚 Sources:  ${SOURCES_FILE}" >&2
echo "" >&2
echo -e "${CYAN}Research Process:${NC}" >&2
echo "  1. Review your research plan in plan.md" >&2
echo "  2. Document findings in findings.md as you research" >&2
echo "  3. Add sources to sources.md with proper citations" >&2
echo "  4. Follow the constitution guidelines in .researchkit/memory/" >&2
echo "" >&2
echo -e "${CYAN}Tips:${NC}" >&2
echo "  • Use web search tools to gather information" >&2
echo "  • Always cite your sources immediately" >&2
echo "  • Note emerging themes and patterns" >&2
echo "  • Document questions that arise" >&2
echo "  • Cross-verify important claims" >&2
echo "" >&2
echo -e "${CYAN}When complete:${NC}" >&2
echo "  Use /researchkit.synthesize to generate final report" >&2
echo "" >&2

# Auto-commit the setup
git add "$RESEARCH_DIR" 2>/dev/null || true
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    git commit -m "research: Begin execution phase for ${RESEARCH_NAME}" 2>/dev/null || true
fi
