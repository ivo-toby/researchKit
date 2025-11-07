#!/usr/bin/env bash
# ResearchKit Synthesize Script - Generate research synthesis

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

show_header "Research Synthesis Phase"

# Check prerequisites
check_git_initialized

# Get current research directory
print_step "Loading research project..."
RESEARCH_DIR=$(get_current_research_dir)
RESEARCH_NAME=$(basename "$RESEARCH_DIR")

print_info "Research Project: ${RESEARCH_NAME}"
print_info "Directory: ${RESEARCH_DIR}"
echo "" >&2

# Check required files exist
PLAN_FILE="${RESEARCH_DIR}/plan.md"
FINDINGS_FILE="${RESEARCH_DIR}/findings.md"
SOURCES_FILE="${RESEARCH_DIR}/sources.md"

MISSING_FILES=0

if [ ! -f "$PLAN_FILE" ]; then
    print_error "Missing: plan.md"
    MISSING_FILES=1
fi

if [ ! -f "$FINDINGS_FILE" ]; then
    print_error "Missing: findings.md"
    MISSING_FILES=1
fi

if [ ! -f "$SOURCES_FILE" ]; then
    print_error "Missing: sources.md"
    MISSING_FILES=1
fi

if [ $MISSING_FILES -eq 1 ]; then
    echo "" >&2
    print_error "Cannot synthesize - required files missing"
    print_info "Complete the execution phase first"
    exit 1
fi

print_success "All research files found"

# Create synthesis.md
SYNTHESIS_FILE="${RESEARCH_DIR}/synthesis.md"

if check_file_exists "$SYNTHESIS_FILE"; then
    print_warning "Synthesis file already exists - will be overwritten"
    echo -n "Continue? [y/N] " >&2
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_info "Synthesis cancelled"
        exit 0
    fi
fi

print_step "Creating synthesis template..."
copy_template "synthesis-template.md" "$SYNTHESIS_FILE"
update_date_in_file "$SYNTHESIS_FILE"

# Extract research topic from plan
RESEARCH_TOPIC=$(grep -m 1 "^# Research Plan:" "$PLAN_FILE" | sed 's/# Research Plan: //')

# Update placeholders
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$SYNTHESIS_FILE"
    sed -i '' "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$SYNTHESIS_FILE"
else
    sed -i "s/\[RESEARCH TOPIC\]/$RESEARCH_TOPIC/g" "$SYNTHESIS_FILE"
    sed -i "s/\[AUTO-GENERATED\]/$RESEARCH_NAME/g" "$SYNTHESIS_FILE"
fi

# Display summary
echo "" >&2
print_success "Synthesis template created!"
echo "" >&2
echo -e "${CYAN}Research Files (Complete):${NC}" >&2
echo "  📋 Plan:      ${PLAN_FILE}" >&2
echo "  📝 Findings:  ${FINDINGS_FILE}" >&2
echo "  📚 Sources:   ${SOURCES_FILE}" >&2
echo "  ${LIGHT_ICON}  Synthesis: ${SYNTHESIS_FILE}" >&2
echo "" >&2
echo -e "${CYAN}Synthesis Guidelines:${NC}" >&2
echo "  1. Extract research question from your plan" >&2
echo "  2. Summarize key findings with citations" >&2
echo "  3. Analyze patterns and themes" >&2
echo "  4. Address conflicting viewpoints" >&2
echo "  5. Draw evidence-based conclusions" >&2
echo "  6. Acknowledge limitations" >&2
echo "  7. Provide actionable recommendations" >&2
echo "" >&2
echo -e "${CYAN}Quality Checklist:${NC}" >&2
echo "  ☐ All claims properly cited" >&2
echo "  ☐ Evidence supports conclusions" >&2
echo "  ☐ Limitations acknowledged" >&2
echo "  ☐ Bibliography complete" >&2
echo "  ☐ Clear answer to research question" >&2
echo "" >&2

# Commit the synthesis setup
git add "$RESEARCH_DIR" 2>/dev/null || true
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    git commit -m "research: Begin synthesis phase for ${RESEARCH_NAME}" 2>/dev/null || true
    print_info "Changes committed to git"
fi

echo "" >&2
print_success "Ready for synthesis!"
print_info "Edit ${SYNTHESIS_FILE} to complete your research"
echo "" >&2
