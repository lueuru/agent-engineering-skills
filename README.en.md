<div align="center">

# AI Agent Engineering Skills

**Fewer AI mistakes, verifiable delivery, self-serviceable environment issues — five skills distilled from real long-running tasks**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](./LICENSE)
![Lang](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87%20%2F%20English-1f6feb?style=flat-square)
![Type](https://img.shields.io/badge/type-agent%20skill-8957e5?style=flat-square)
[![Last commit](https://img.shields.io/github/last-commit/lueuru/agent-engineering-skills?style=flat-square)](https://github.com/lueuru/agent-engineering-skills/commits)

**[English](#) · [中文](./README.md)**

</div>

---

## What is this

Five **AI Agent Skills**. They don't solve business problems — they solve
**"AI work itself being unreliable"**:

| Pain point | Typical symptom | Skill |
|---|---|---|
| All criteria green — but they're verifying the wrong code | "Tests all passed" → production is still broken | `verify-criteria-selfcheck` |
| Repo homepage is thin | A three-line README, no badges, no structure | `github-repo-beautify` |
| "Let me clean your disk" | Scans then deletes, irreversible | `windows-cleanup-audit` |
| Agent client won't start | A pile of plugin load errors, no idea where to begin | `dsh-profile-repair` |
| Long sessions need review | Session files are zstd-compressed JSONL, unreadable | `dsh-session-log-analysis` |

The first three are **general-purpose** (any project); the last two are
**environment-specific** troubleshooting skills (DeepSeek Harness Desktop).

## Skill list

### General-purpose

#### 1. `verify-criteria-selfcheck` — harden acceptance criteria against false passes

Adds a self-check layer on top of acceptance criteria / automated tests. Use it when:

- **All green but verifying different code** (criteria run on a temp copy while you edit the source)
- **Checklists never match** (wrong regex, always-false type comparison, `array == 0` is always false)
- **The criterion itself is wrong but outputs confident results** — the worst class: more dangerous than having no criteria
- Cleanup / migration / CI verification scripts need hardening

The core is **true counter-evidence**: after writing a criterion, **break it on purpose once**
and confirm it actually goes red. Without that step, the word "passed" carries no weight.

#### 2. `github-repo-beautify` — repository homepage beautification

Polish a GitHub repo homepage and README: layout, status badges, stat cards, cover art,
collapsible TOC, theme colors, contributor display; also generates social preview images and
configures repo metadata (description / homepage / topics).

Two pieces of hard-won knowledge built in:
- A **third-party service survival list** (which image/stat services are still alive, tested —
  so you never recommend a dead one)
- The **"shields.io green illusion" criterion** — when a badge service errors it returns
  **HTTP 200 with a normal-looking image that says `badge not found`**; status-code-only
  checks will believe everything is fine

#### 3. `windows-cleanup-audit` — Windows disk cleanup audit

Handles "clean up my computer / C: drive full / remove junk" requests.

The enforced workflow is **read-only scan first**, then:

- **Protection list**: non-regenerable project assets (keystores, base packages, signers) never
  enter the deletion list
- **Guardrail behavior**: Temp dirs are deletable, but personal-directory deletions are forced
  through the recycle bin and fail closed
- **Escape hatch**: when guardrails block automation, generate a script for the user to run
  themselves instead of bypassing the guardrail
- Documents machine-specific traps (PowerShell swallowing stdout, nested `.ps1` silently
  no-op'ing, security policy blocking certain command keywords) plus one real root-cause case

### Environment-specific (DeepSeek Harness Desktop)

#### 4. `dsh-profile-repair` — DSH startup failure repair

For DSH desktop failures: plugins/sessions vanishing from the Web UI, or errors like
`.credentials.yaml.lock`, `timed out waiting for the writer lock`, `assertEntriesActivated`,
`Failed to load plugins`.

The skill maps **six known failure modes** with their fixes. The most overlooked one:
**a stale `.credentials.yaml.lock` blocks every startup** (check it first).

#### 5. `dsh-session-log-analysis` — DSH session log analysis

Point it at a DSH session directory (`session-*/session.jsonl.zstd`) for
**learning / reading / analysis / summarization / review**:

- zstd decompression
- The **real JSONL event schema** (fields are `user/message`, not the assumed `user` —
  guess the name wrong and nothing parses)
- How to summarize long sessions (via compaction / summary events)
- Produces a handoff-ready "learning map"

## Install

```bash
git clone https://github.com/lueuru/agent-engineering-skills.git
cp -r agent-engineering-skills/skills/* ~/.workbuddy/skills/
```

Just one:

```bash
cp -r agent-engineering-skills/skills/verify-criteria-selfcheck ~/.workbuddy/skills/
```

> The two `dsh-*` skills target a specific installation; their paths and versions belong to
> that environment and need adjusting on a different machine.

## Usage examples

**Example 1: tests all green, problem persists**

> "My check scripts all pass, but production is still broken."

`verify-criteria-selfcheck` first checks three things: whether the criteria run against this
code, whether any checklist expression is always-true/false, and whether the object under
test is still used by the product at all.

**Example 2: repo homepage too bare**

> "Make this repo's README look decent."

`github-repo-beautify` rewrites the README layout, adds badges and a TOC, generates a social
preview, and configures the repo description and topics.

**Example 3: disk cleanup, afraid of deleting the wrong thing**

> "C: drive is full, help me clean it."

`windows-cleanup-audit` **scans read-only first and produces a report** listing deletables and
protected items — it does **not** delete anything on its own.

## Where these skills come from

Not written from theory — **bitten repeatedly by the same class of failure across a
multi-month real project**:

- 40 criteria all green while the live page showed test placeholder content to visitors
- A high-quality backup script that was **never scheduled** (latest backup was a month old)
- An "optimization" (adding `defer` to a script) that crashed the whole page while curl and
  status codes all read 200
- A rule written, syntax-checked, **and permanently ineffective** (inserted in the wrong
  position, becoming a child block of another rule)

The common thread: **these failures make no sound**. That's why these skills focus not on
"how to do it" but on **"how to confirm you actually did it right"**.

## Related repositories

- **[game-modding-skills](https://github.com/lueuru/game-modding-skills)** — Six skills for modding legacy Unity Android games — in-place dex patching, channel SDK stripping, emulator verification, and the localization trio (DLL / asset text / Chinese fonts)

## License

[MIT](./LICENSE) — free to use, modify, and redistribute; keep the copyright notice.

</div>
