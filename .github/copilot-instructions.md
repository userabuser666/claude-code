Purpose
-------
This file gives concise, project-specific instructions to AI coding agents so they can be immediately productive in this repository. Focus on the plugin system, `hookify` rules, and how hooks are executed.

Quick overview (big picture)
----------------------------
- This repo powers the Claude Code CLI and a set of official plugins under `plugins/`.
- Plugins follow a consistent layout: a `.claude-plugin/plugin.json` metadata file plus optional `commands/`, `agents/`, `skills/`, `hooks/`, and `README.md` (see `plugins/README.md`).
- The `hookify` plugin enforces conversational/workflow rules by loading markdown rule files from `.claude/hookify.*.local.md`, parsing YAML frontmatter, and evaluating them with a rule engine before/after tool use.

Key files to read first
----------------------
- Top-level README: `README.md` — high level project purpose and plugin list.
- Plugin docs: `plugins/README.md` — shows standard plugin structure and examples.
- Hookify parser: `plugins/hookify/core/config_loader.py` — how rule frontmatter is parsed (legacy `pattern` vs `conditions`).
- Hookify engine: `plugins/hookify/core/rule_engine.py` — how conditions/operators are evaluated and what output shapes mean (`systemMessage`, `hookSpecificOutput`, `permissionDecision`).
- Hook entrypoints: `plugins/hookify/hooks/*.py` (e.g. `pretooluse.py`) — how hooks are invoked and expected to return JSON on stdout.

Important conventions and patterns (do this when editing/adding code)
-----------------------------------------------------------------
- Rule files: Place markdown files in `.claude/` and start with `---` YAML frontmatter. Frontmatter can contain either a legacy `pattern` (regex) or a `conditions` list with `field`, `operator`, `pattern` entries. See `config_loader.extract_frontmatter()` for parsing quirks.
- Operators: The rule engine supports `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with`. Use `regex_match` for flexible matching; regexes are compiled with case-insensitive flags and cached.
- Hook outputs: Hook scripts MUST print JSON to stdout and should not raise non-zero exit codes that block workflows. `pretooluse.py` demonstrates returning `{}` when no match and structured `systemMessage` or `hookSpecificOutput` when rules match.
- Imports & runtime: Hook scripts expect `CLAUDE_PLUGIN_ROOT` env var to be set; scripts add the plugin root and its parent to `sys.path` so `from hookify.core...` works. Preserve this pattern when adding new hook scripts.
- Error handling: Hooks prefer to allow operations on unexpected errors (they log via `systemMessage` and exit 0). Maintain this fail-open behavior.

Developer workflows & quick commands
----------------------------------
- Local test of a hook script (example):

```bash
# Create a test input: input.json
# {"tool_name":"Bash","tool_input":{"command":"rm -rf /tmp/x"}}
cat input.json | python plugins/hookify/hooks/pretooluse.py
```

- Rule file unit tests: Many core Python modules include `if __name__ == '__main__'` blocks that can be run directly for quick sanity checks (see `config_loader.py` and `rule_engine.py`).

Integration points & API shapes
------------------------------
- Tool hooks read JSON on stdin and return JSON on stdout. The hook engine expects keys like `tool_name`, `tool_input`, `hook_event_name`, `transcript_path`, etc.
- When blocking, `rule_engine.evaluate_rules()` returns objects with `decision: "block"` or `hookSpecificOutput.permissionDecision: "deny"` for PreToolUse/PostToolUse.

Project-specific conventions (do not assume typical defaults)
---------------------------------------------------------
- Plugins live under `plugins/` and are intended to be portable; avoid hard-coding absolute paths — use `CLAUDE_PLUGIN_ROOT` if needed.
- YAML frontmatter parser is permissive but custom: multi-line list-dict styles are parsed by `config_loader.extract_frontmatter()`; prefer simple explicit `conditions` lists for new rules.
- Hooks are designed to never abort the main CLI if they themselves crash — they should log errors but exit 0.

Where to make changes
---------------------
- Rule format changes: `plugins/hookify/core/config_loader.py`
- Matching/evaluation behavior: `plugins/hookify/core/rule_engine.py`
- Hook wiring and invocation behavior: `plugins/hookify/hooks/*.py` and callers that invoke those scripts (search for `CLAUDE_PLUGIN_ROOT` usage)

Examples to copy/paste
----------------------
- Minimal rule frontmatter (legacy pattern):

```yaml
---
name: warn-rm
enabled: true
event: bash
pattern: "rm\s+-rf"
---

⚠️ Dangerous `rm -rf` detected
```

- Modern rule with conditions:

```yaml
---
name: forbid-eval
enabled: true
event: file
conditions:
  - field: new_text
    operator: regex_match
    pattern: "\\beval\\("   # note: escape backslashes in markdown
action: block
---

Blocking `eval()` usage in new file edits
```

Questions for you
-----------------
- Are there other runtime entrypoints (MCP servers, dev containers, tests) you want me to document here?
- Do you want stricter linting or testing guidance included (e.g. preferred Python versions, formatters)?

If this looks good I will commit this file; tell me any additions or corrections and I will iterate.
