---
name: dsh-session-log-analysis
description: This skill should be used when the user points at a DSH (DeepSeek Harness Desktop) sessions directory (e.g. `Desktop/sessions/`, `~/.dsh/sessions/`, or any folder of `session-*/session.jsonl.zstd`) and asks to 学习 / 阅读 / 分析 / 总结 / 复盘 past conversations — including "把这些会话学一下", "看看我以前聊了什么", "恢复上下文", "写交接总结", or when prior-session context is needed but `conversation_search` cannot reach it (e.g. sessions copied out of the live DSH home). Covers zstd decompression, the real JSONL event schema (user/message NOT user), long-session digesting via compaction/summary, and producing a handover-grade 学习地图.
agent_created: true
---

# dsh-session-log-analysis

Turn a directory of DSH session logs into (a) readable transcripts and (b) a handover-grade synthesis — without drowning in the ~1M-token noise those files contain.

## Why this needs a skill

A single DSH session JSONL is 60–70 MB decompressed, and **~95% of it is noise** for comprehension purposes: `reasoning-chunks`, `assistant/chunk`, `tool-call-chunks` (token-by-token deltas), and `request/header` (a full 60 KB system prompt repeated per request). Naive `Read` will blow the context window on one file. The pipeline below reduces 160 MB → a few hundred KB of signal.

## Step 0 — Setup (once per machine)

`zstandard` is not stdlib. Use the managed venv (never global pip):

```bash
PY_DIR="C:/Users/Administrator/.workbuddy/binaries/python/envs/default"
"C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe" -m venv "$PY_DIR"
"$PY_DIR/Scripts/pip.exe" install zstandard      # run_in_background=true, takes ~35s
PY="$PY_DIR/Scripts/python.exe"
```

## Step 1 — Survey (decompress + metadata)

Decompress every `*.zstd` and emit a per-session summary: type histogram, cwd, createdAt, line count. Script: `scripts/survey.py` (see below). Run it with stdout redirected to a file, then read only that JSON.

```bash
"$PY" survey.py > _session_survey.json
```

**Read the survey before anything else.** It tells you which sessions are empty shells (`{"type":"session"}` + 4 header events only → ignore) and which are huge (prioritize by `lines`).

## Step 2 — Schema facts you MUST know

Getting these wrong costs a whole extra pass:

| Fact | Detail |
|---|---|
| Real message types | `user/message` and `assistant/message` — **there is no `user` type** |
| Payload nesting | almost everything is under `data`; `assistant/message` → `data.message.content[]` |
| Text extraction | walk `content[]` and concatenate items with `type == "text"` |
| Tool activity | `tool/call` (`data.name` / `data.arguments`) + `tool/result` (`data.message.content[].content[].text`) |
| Long-session gold | `compaction/summary` — a full LLM-written checkpoint of everything before it. **Always read these first for long sessions.** |
| Goal tracking | `goal/change` → `data.operation` (`create`/`complete`) + `data.goal.objective` |
| Titles | `session/title` → `data.title` (may appear more than once; first is the original, later ones are LLM-regenerated) |
| Timestamps | ms epoch in `time` (per-event) and `createdAt` (session) |
| cwd encoding | directory names escape the path: `--C-Users-Administrator-Desktop-~5C0F~7A0B~5E8F--` = `…\Desktop\小程序` |
| Plugin noise | `source.kind == "plugin"` on `user/message` = injected runtime context, **not** the human. Filter it out or you will read the same rules block 50 times. |

## Step 3 — Two-tier extraction

Both scripts should be **streaming line-by-line** (`for raw in f:` with `json.loads` per line) — never `read()` the whole file into memory beyond what the decompressor yields, and never `json.dumps` intermediate objects you don't need.

**Tier A — full transcript** (`ASSIST_LIMIT` env, default 1500 chars per assistant msg): user messages, assistant text, tool calls with truncated args, truncated tool results. Use for sessions you will actually read (≤ ~100 KB output).

**Tier B — digest** (for sessions >10 MB compressed): only human user messages (skip `source.kind == "plugin"`), `compaction/summary` (up to 8000 chars each), and `goal/change`. Typical result: a 65 MB session → 35 KB digest. **This is the highest signal-per-token artifact in the whole pipeline.**

Run Tier B on the big ones and read those digests instead of the transcripts.

## Step 4 — Report structure that works

Users asking to "学习" a sessions folder want a **handover document**, not a chat log recap. Proven shape:

1. **总览表** — one row per session: id prefix / cwd / line count / topic. Groups the corpus at a glance.
2. **Per-project main lines** — goal, hard constraints/rules the user set, key assets (paths), then the technical meat.
3. **The root-cause tables** — bug → consequence → correct fix. This is what the user actually re-reads later.
4. **Current unresolved state + to-do checkboxes** — explicitly mark what is NOT closed, and what the last interaction was.
5. **Cross-session patterns** — how the user works (feedback style, what they punish), and reusable methodology.
6. **Appendix: how to reproduce** — the exact commands + the schema table, so the next session doesn't re-derive it.

## Pitfalls learned the hard way

- Output must go to files, then be `Read`. Do not pipe large script output straight into the conversation.
- A 65 MB transcript is ~1.1 MB of markdown and ~5,000 lines — **do not read it linearly**; grep the digest, then read the tail of the transcript for the final state.
- Duplicate sessions are common (same thread archived twice, byte-identical). The survey's identical `lines` + `types` histogram reveals them — analyze one and say so.
- `session.jsonl.zstd` files are append-only logs of a *live* product; the last user message is often hours after the last assistant reply. Report the tail honestly ("会话在此结束，未闭环").
- If the user only says "学习" with no question, they still expect a **deliverable** — write the report to a file and `present_files` it.
- The identity/context block injected at session start (`plugin` messages) is a **goldmine** for reconstructing rules the user set in other sessions — mine it for the long-term memory items, don't just skip it.

## Reference implementation

`scripts/` holds the three working scripts (survey / extract / digest). They were validated against a 12-session, 143k-line corpus on Windows. Copy and adapt rather than rewriting; the schema handling is the expensive part.
