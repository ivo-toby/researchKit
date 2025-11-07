#!/usr/bin/env bash
# Common utilities for ResearchKit scripts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji support
CHECK_MARK="✓"
CROSS_MARK="✗"
RESEARCH_ICON="🔬"
BOOK_ICON="📚"
WRITE_ICON="✍️"
LIGHT_ICON="💡"

# Print colored output
print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

print_step() {
    echo -e "${BLUE}→ $1${NC}"
}

# Get the ResearchKit root directory
get_researchkit_root() {
    if [ -d ".researchkit" ]; then
        echo "$(pwd)/.researchkit"
    else
        print_error "Not in a ResearchKit project directory"
        print_info "Run 'research init' to initialize a project"
        exit 1
    fi
}

# Get the current research project directory from git branch
get_current_research_dir() {
    local researchkit_root=$(get_researchkit_root)
    local branch_name=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

    if [ -z "$branch_name" ] || [ "$branch_name" = "main" ] || [ "$branch_name" = "master" ]; then
        print_error "Not on a research branch"
        print_info "Use /researchkit.plan to start a new research project"
        exit 1
    fi

    # Extract research ID from branch name (e.g., research/001-topic -> 001-topic)
    local research_id=$(echo "$branch_name" | sed 's|^research/||')
    local research_dir="${researchkit_root}/research/${research_id}"

    if [ ! -d "$research_dir" ]; then
        mkdir -p "$research_dir"
    fi

    echo "$research_dir"
}

# Get the next research ID
get_next_research_id() {
    local researchkit_root=$(get_researchkit_root)
    local research_dir="${researchkit_root}/research"

    # Find the highest existing research number
    local max_id=0
    for dir in "${research_dir}"/*/; do
        if [ -d "$dir" ]; then
            local dir_name=$(basename "$dir")
            local id=$(echo "$dir_name" | grep -oE '^[0-9]+' || echo "0")
            if [ "$id" -gt "$max_id" ]; then
                max_id=$id
            fi
        fi
    done

    # Increment and format with leading zeros
    printf "%03d" $((max_id + 1))
}

# Create a new research project
create_research_project() {
    local topic="$1"
    local researchkit_root=$(get_researchkit_root)

    if [ -z "$topic" ]; then
        print_error "Research topic is required"
        exit 1
    fi

    # Generate research ID and directory name
    local research_id=$(get_next_research_id)
    local topic_slug=$(echo "$topic" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd '[:alnum:]-')
    local research_name="${research_id}-${topic_slug}"
    local research_dir="${researchkit_root}/research/${research_name}"

    # Create research directory
    mkdir -p "$research_dir"

    # Create git branch
    local branch_name="research/${research_name}"
    git checkout -b "$branch_name" 2>/dev/null || git checkout "$branch_name"

    print_success "Created research project: ${research_name}"
    print_info "Branch: ${branch_name}"

    echo "$research_dir"
}

# Copy template file
copy_template() {
    local template_name="$1"
    local destination="$2"
    local researchkit_root=$(get_researchkit_root)
    local template_file="${researchkit_root}/templates/${template_name}"

    if [ ! -f "$template_file" ]; then
        print_error "Template not found: ${template_name}"
        exit 1
    fi

    cp "$template_file" "$destination"
    print_success "Created: $(basename $destination)"
}

# Check if file exists
check_file_exists() {
    local file="$1"
    local file_name=$(basename "$file")

    if [ -f "$file" ]; then
        print_warning "${file_name} already exists"
        return 0
    else
        return 1
    fi
}

# Update file with current date
update_date_in_file() {
    local file="$1"
    local current_date=$(date +%Y-%m-%d)

    # Replace [DATE] placeholders with current date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/\[DATE\]/$current_date/g" "$file"
    else
        # Linux
        sed -i "s/\[DATE\]/$current_date/g" "$file"
    fi
}

# Display ResearchKit header
show_header() {
    local title="$1"
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║              ${RESEARCH_ICON}  ResearchKit                            ║"
    echo "║                                                            ║"
    echo "║              $title"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verify git is initialized
check_git_initialized() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not a git repository"
        print_info "Initialize git with: git init"
        exit 1
    fi
}

# Get template directory
get_template_dir() {
    local researchkit_root=$(get_researchkit_root)
    echo "${researchkit_root}/templates"
}

# Export functions
export -f print_success
export -f print_error
export -f print_warning
export -f print_info
export -f print_step
export -f get_researchkit_root
export -f get_current_research_dir
export -f get_next_research_id
export -f create_research_project
export -f copy_template
export -f check_file_exists
export -f update_date_in_file
export -f show_header
export -f check_git_initialized
export -f get_template_dir
