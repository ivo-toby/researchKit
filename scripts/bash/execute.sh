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
echo ""

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

echo ""
print_success "Research execution environment ready!"
echo ""
echo -e "${CYAN}Research Files:${NC}"
echo "  📋 Plan:     ${PLAN_FILE}"
echo "  📝 Findings: ${FINDINGS_FILE}"
echo "  📚 Sources:  ${SOURCES_FILE}"
echo ""
echo -e "${CYAN}Research Process:${NC}"
echo "  1. Review your research plan in plan.md"
echo "  2. Document findings in findings.md as you research"
echo "  3. Add sources to sources.md with proper citations"
echo "  4. Follow the constitution guidelines in .researchkit/memory/"
echo ""
echo -e "${CYAN}Tips:${NC}"
echo "  • Use web search tools to gather information"
echo "  • Always cite your sources immediately"
echo "  • Note emerging themes and patterns"
echo "  • Document questions that arise"
echo "  • Cross-verify important claims"
echo ""
echo -e "${CYAN}When complete:${NC}"
echo "  Use /researchkit.synthesize to generate final report"
echo ""

# Auto-commit the setup
git add "$RESEARCH_DIR" 2>/dev/null || true
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    git commit -m "research: Begin execution phase for ${RESEARCH_NAME}" 2>/dev/null || true
fi
