# Ollama Agent Conversational Redesign Plan

## Problem Statement

The current Ollama agent implementation uses a rigid 4-phase workflow (constitution → plan → execute → synthesize) that is not conversational or interactive enough. Users want a natural chat-like interface similar to Claude Code, OpenCode, or Gemini CLI, but focused on research instead of coding.

### Current Issues

1. **Rigid workflow**: Users must go through all 4 phases sequentially
2. **No natural conversation**: Can't ask follow-up questions or have a dialogue
3. **Static process**: No ability to iterate or refine research interactively
4. **Single-shot**: One topic, one workflow, then exit
5. **Poor UX**: Approval loops are clunky, not conversational

### Desired Experience

```
$ research-ollama

ResearchKit Ollama Agent v0.2.0
Conversational research assistant using local Ollama models

Connected to: llama3.2 at http://localhost:11434
Type /help for commands, /exit to quit

You: Tell me about quantum computing applications in 2024

🔍 Searching the web...
📄 Reading: https://quantuminsider.com/2024-trends
📄 Reading: https://nature.com/quantum-computing

Agent: Based on my research, quantum computing in 2024 has several key applications:

1. **Drug Discovery**: Companies like IonQ are using quantum computers to simulate
   molecular interactions...

2. **Cryptography**: Post-quantum cryptography standards were finalized in 2024...

3. **Financial Modeling**: JPMorgan and IBM are using quantum computing for...

Sources:
- https://quantuminsider.com/2024-trends
- https://nature.com/quantum-computing

You: Can you tell me more about the drug discovery applications?

Agent: Absolutely! Let me look into that more deeply...

🔍 Searching: quantum computing drug discovery 2024
📄 Reading: https://pharmatech.com/quantum-drug-discovery

[Conversation continues naturally...]

You: /save

💾 Saved conversation to: research/quantum-computing-2024/conversation.md
📚 Sources saved to: research/quantum-computing-2024/sources.md

You: /exit

Goodbye! Your research has been saved.
```

---

## Architecture Changes

### 1. New Conversational Loop (Core Change)

**Current Architecture:**
```
CLI → Environment Check → Config → Workflow → [Constitution → Plan → Execute → Synthesize]
```

**New Architecture:**
```
CLI → Environment Check → Config → ChatSession → [Message Loop with Tools]
                                                    ↓
                                    [Auto-save conversation, sources, findings]
```

### 2. Component Changes

#### A. CLI (`cli.py`) - MAJOR REFACTOR

**Remove:**
- Topic prompt
- Workflow orchestrator initialization
- Single-shot execution

**Add:**
- Session management
- Chat loop
- Command processing (`/help`, `/save`, `/clear`, `/sources`, `/export`, `/exit`)
- Streaming support
- Auto-save on exit

**New Structure:**
```python
def main():
    # 1. Setup (same as current)
    - Environment checks
    - Config loading
    - Ollama connection

    # 2. Session initialization (NEW)
    - Load or create session
    - Display session info

    # 3. Chat loop (NEW)
    while True:
        user_input = prompt_user()

        if user_input.startswith('/'):
            handle_command(user_input)
            continue

        # Generate response with tools
        response = agent.chat(user_input)

        # Display response with streaming
        display_response(response)

        # Auto-save conversation
        session.save()
```

#### B. Chat Session (`chat_session.py`) - NEW MODULE

Manages persistent research sessions with conversation history.

**Features:**
- Create new session or load existing
- Session metadata (topic, created_at, updated_at)
- Conversation history storage
- Source tracking (URLs visited)
- Findings accumulation
- Export to markdown

**Storage Structure:**
```
.researchkit/
  sessions/
    active.json                     # Current active session
    quantum-computing-2024/
      session.json                  # Metadata
      conversation.json             # Full conversation history
      conversation.md               # Human-readable export
      sources.md                    # All sources cited
      findings.md                   # Key findings extracted
```

**API:**
```python
class ChatSession:
    def __init__(self, session_id: str = None)
    def add_message(self, role: str, content: str)
    def add_tool_use(self, tool_name: str, args: dict, result: dict)
    def add_source(self, url: str, title: str = "")
    def save(self) -> bool
    def export_to_markdown(self) -> Path
    def get_conversation_context(self, max_tokens: int) -> List[Dict]
    def clear(self) -> bool
```

#### C. Conversational Agent (`conversational_agent.py`) - NEW MODULE

Replaces `WorkflowOrchestrator`. Handles natural conversation with automatic tool use.

**Features:**
- Natural language understanding
- Automatic tool selection (web_search, fetch_url, parse_pdf)
- Streaming responses
- Source extraction and tracking
- Context management (prevent token overflow)

**API:**
```python
class ConversationalAgent:
    def __init__(self, client, config, tool_registry, tool_definitions, session)

    def chat(self, user_message: str, stream: bool = True) -> str:
        """Process user message and generate response with tools."""

    def _generate_with_tools(self, messages) -> Generator[str, None, None]:
        """Generate response with automatic tool calling (streaming)."""

    def _execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute research tool and track sources."""

    def _extract_sources(self, tool_result: dict) -> List[str]:
        """Extract URLs from tool results for source tracking."""
```

#### D. Conversation Engine (`conversation.py`) - MODIFY

**Keep:**
- Tool execution loop
- Tool registry management
- Message management

**Remove:**
- `approval_loop()` - No longer needed
- Rigid prompting structure

**Simplify:**
Focus on core conversation + tool execution, without approval loops.

#### E. Command Handler (`commands.py`) - NEW MODULE

Handles slash commands for session management.

**Commands:**
- `/help` - Show available commands
- `/save` - Save current conversation
- `/clear` - Clear conversation (keep session)
- `/new [topic]` - Start new research session
- `/sessions` - List available sessions
- `/load <session>` - Load previous session
- `/sources` - Show all sources
- `/findings` - Show extracted findings
- `/export` - Export to markdown
- `/config` - Show/edit configuration
- `/exit` or `/quit` - Save and exit

**API:**
```python
class CommandHandler:
    def __init__(self, session, agent, config)

    def handle(self, command: str) -> bool:
        """Handle command, return True if should exit."""

    def _cmd_help(self)
    def _cmd_save(self)
    def _cmd_clear(self)
    def _cmd_new(self, topic: str)
    # ... etc
```

#### F. UI/Display (`display.py`) - NEW MODULE

Handles rich terminal output for chat interface.

**Features:**
- Streaming text display (like Claude Code)
- Tool use indicators (🔍 Searching, 📄 Reading, etc.)
- Source citations inline
- Markdown rendering
- Progress indicators
- Syntax highlighting for code blocks

**API:**
```python
class ChatDisplay:
    def __init__(self, console: Console)

    def show_user_message(self, message: str)
    def show_agent_message(self, message: str, stream: bool = True)
    def show_tool_use(self, tool_name: str, args: dict)
    def show_tool_result(self, tool_name: str, success: bool)
    def show_sources(self, sources: List[str])
    def show_error(self, error: str)
    def prompt_user(self) -> str
```

---

## Implementation Plan

### Phase 1: Core Conversational Loop (Day 1-2)

**Goal**: Replace rigid workflow with natural chat loop

1. **Create `chat_session.py`**
   - Session data structures
   - Conversation storage (JSON + Markdown)
   - Source tracking
   - Save/load functionality

2. **Create `conversational_agent.py`**
   - Port tool execution from `ConversationEngine`
   - Add streaming support
   - Implement source extraction
   - Add context management (sliding window for long conversations)

3. **Refactor `cli.py`**
   - Remove workflow orchestrator
   - Add chat loop
   - Integrate session management
   - Basic command support (/exit)

4. **Testing**
   - Basic conversation works
   - Tools are called automatically
   - Conversation is saved

### Phase 2: Commands & Session Management (Day 3)

**Goal**: Add session management and commands

1. **Create `commands.py`**
   - Implement all slash commands
   - Session switching
   - Export functionality

2. **Update `cli.py`**
   - Integrate command handler
   - Session listing and loading
   - Command autocomplete (optional)

3. **Testing**
   - All commands work
   - Sessions persist correctly
   - Export generates proper markdown

### Phase 3: Enhanced UX (Day 4)

**Goal**: Make it feel like Claude Code

1. **Create `display.py`**
   - Streaming message display
   - Tool use indicators (emoji + text)
   - Source citations
   - Progress spinners

2. **Add streaming to agent**
   - Stream from Ollama API
   - Display tokens as they arrive
   - Handle tool calls mid-stream

3. **Polish CLI**
   - Better prompts
   - Colors and formatting
   - Error handling
   - Keyboard interrupt handling

4. **Testing**
   - Smooth streaming experience
   - No visual glitches
   - Professional appearance

### Phase 4: Advanced Features (Day 5)

**Goal**: Add power user features

1. **Multi-turn research**
   - Context summarization for long conversations
   - Automatic findings extraction
   - Intelligent source management

2. **Session analytics**
   - Token usage tracking
   - Tool usage statistics
   - Time spent

3. **Export formats**
   - Markdown (default)
   - JSON (for programmatic use)
   - HTML (with styling)

4. **Configuration**
   - Change model mid-session
   - Adjust temperature
   - Configure tool behavior

### Phase 5: Testing & Documentation (Day 6)

**Goal**: Production-ready release

1. **Comprehensive testing**
   - Unit tests for new modules
   - Integration tests for chat loop
   - E2E tests with real Ollama

2. **Update documentation**
   - New conversational UX guide
   - Command reference
   - Session management guide
   - Migration guide from old workflow

3. **Polish**
   - Bug fixes
   - Performance optimization
   - Memory management

---

## File Structure Changes

### New Files

```
src/ollama_agent/
  chat_session.py          # Session management
  conversational_agent.py  # Main chat agent
  commands.py              # Slash command handler
  display.py               # Rich terminal UI
  streaming.py             # Streaming utilities (optional)
```

### Modified Files

```
src/ollama_agent/
  cli.py                   # Major refactor to chat loop
  conversation.py          # Simplify, remove approval loops
  __init__.py              # Update exports
```

### Deprecated Files (Keep for reference, don't import)

```
src/ollama_agent/
  workflow.py              # Replace with conversational_agent.py
  prompts/                 # Not needed for conversational style
    constitution.py
    plan.py
    execute.py
    synthesize.py
```

### New Storage Structure

```
.researchkit/
  config/
    ollama.json            # Existing
  sessions/                # NEW
    active.json            # Current active session ID
    <session-id>/
      session.json         # Metadata
      conversation.json    # Full history
      conversation.md      # Export
      sources.md           # Sources
      findings.md          # Findings
```

---

## Breaking Changes

### For Users

1. **No more 4-phase workflow**
   - Old: Run command → go through phases → exit
   - New: Run command → enter chat → ask questions → /exit

2. **Session-based**
   - Conversations persist across sessions
   - Must explicitly start new session with `/new`

3. **No approval loops**
   - Agent responds directly
   - User can interrupt or ask for clarification

4. **Command-based actions**
   - Saving: `/save` instead of automatic after each phase
   - Exiting: `/exit` instead of automatic after synthesis

### For Developers

1. **`WorkflowOrchestrator` deprecated**
   - Use `ConversationalAgent` instead

2. **Different storage structure**
   - Sessions instead of numbered research folders
   - JSON + Markdown instead of just Markdown

3. **New entry point flow**
   - Chat loop instead of workflow execution

---

## Migration Strategy

### Option 1: Clean Break (Recommended)

- Bump version to `0.2.0` (breaking change)
- Keep old code in `ollama_agent/legacy/` for reference
- Update all documentation
- Provide migration guide

### Option 2: Compatibility Mode

- Add flag `--legacy` to use old workflow
- Default to new conversational mode
- Deprecation warning for `--legacy`
- Remove in `0.3.0`

**Recommendation**: Option 1 (clean break) because:
- Simpler codebase
- Better UX from day one
- Old workflow is fundamentally different
- No existing users to migrate yet (new feature)

---

## Success Criteria

### User Experience

- [ ] Feels like chatting with Claude Code, but for research
- [ ] Natural conversation flow without rigid phases
- [ ] Can ask follow-up questions and iterate
- [ ] Responses stream naturally
- [ ] Tool use is visible but non-intrusive
- [ ] Sessions persist and can be resumed

### Technical

- [ ] All tools (web_search, fetch_url, parse_pdf) work seamlessly
- [ ] Conversation history is properly managed
- [ ] Sources are automatically tracked
- [ ] Export generates clean markdown
- [ ] Memory efficient (context window management)
- [ ] No blocking operations (async where possible)

### Documentation

- [ ] Clear usage guide with examples
- [ ] Command reference
- [ ] Session management explained
- [ ] Migration guide from old workflow
- [ ] Video demo (optional)

---

## Timeline

- **Day 1-2**: Core conversational loop (Phase 1)
- **Day 3**: Commands & sessions (Phase 2)
- **Day 4**: Enhanced UX (Phase 3)
- **Day 5**: Advanced features (Phase 4)
- **Day 6**: Testing & docs (Phase 5)

**Total**: 6 days for complete implementation

---

## Open Questions

1. **Auto-save frequency**: After every message? On /save only? On exit only?
   - **Recommendation**: After every agent response (non-intrusive, prevents data loss)

2. **Context window management**: How to handle conversations that exceed model context?
   - **Recommendation**: Sliding window + optional summarization of old messages

3. **Multi-session handling**: Allow multiple active sessions?
   - **Recommendation**: One active session at a time, but can /load others

4. **Tool auto-execution**: Should agent always execute tools or ask first?
   - **Recommendation**: Always execute (conversational agents like Claude Code do this)

5. **Interrupt handling**: What if user wants to stop tool execution mid-stream?
   - **Recommendation**: Ctrl+C stops current operation, returns to prompt

6. **Findings extraction**: Automatic or manual?
   - **Recommendation**: Automatic but non-blocking (background process)

---

## Dependencies

### New Dependencies

- None! All features can be built with existing dependencies.

### Optional Enhancements

- `prompt_toolkit` - Advanced input with autocomplete, history
- `aiohttp` - Async HTTP for faster tool execution
- `asyncio` - Async streaming

**Recommendation**: Start without new dependencies, add if needed.

---

## Risk Assessment

### Low Risk

- Session management (well-understood pattern)
- Command handling (straightforward)
- Display improvements (cosmetic)

### Medium Risk

- Streaming implementation (complexity in handling tool calls)
- Context window management (need careful testing)
- Memory leaks in long conversations (needs profiling)

### Mitigation

- Extensive testing with long conversations
- Memory profiling tools
- Graceful degradation (fallback to non-streaming if issues)

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Approve architectural changes**
3. **Begin Phase 1 implementation**
4. **Iterate based on feedback**

---

## Appendix: Example Commands

```bash
# Start agent
$ research-ollama

# In chat
You: /help
You: /new quantum computing trends 2024
You: Tell me about recent breakthroughs
Agent: [Response with tools]
You: Can you find more recent sources?
Agent: [More research]
You: /sources
You: /save
You: /export
You: /exit

# Resume session
$ research-ollama --load quantum-computing-trends-2024

# Or use command
You: /sessions
You: /load quantum-computing-trends-2024
```

---

**Version**: 1.0
**Author**: Claude
**Date**: 2025-11-09
