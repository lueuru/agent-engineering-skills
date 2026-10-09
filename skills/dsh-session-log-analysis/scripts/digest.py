# -*- coding: utf-8 -*-
"""Tier B extractor: digests for long sessions.

Outputs only the high-signal events (human user messages, compaction/summary,
goal/change, titles) so a 65 MB session collapses into ~35 KB of markdown.

Usage:
    python digest.py                    # auto: every session whose .jsonl > MIN_MB
    python digest.py --all              # every session
    python digest.py session-abc123 ... # explicit session-id prefixes

Env:
    DUMP     input dir of *.jsonl        (default: ./_session_dump)
    OUT      output dir for *.digest.md  (default: ./_session_transcripts)
    MIN_MB   size threshold in MB        (default: 2)
    SUMM_CAP max chars per compaction summary (default: 8000)
    MSG_CAP  max chars per user message       (default: 2500)
"""
import json, os, io, sys, datetime

DUMP = os.environ.get('DUMP', '_session_dump')
OUT = os.environ.get('OUT', '_session_transcripts')
MIN_MB = float(os.environ.get('MIN_MB', '2'))
SUMM_CAP = int(os.environ.get('SUMM_CAP', '8000'))
MSG_CAP = int(os.environ.get('MSG_CAP', '2500'))

os.makedirs(OUT, exist_ok=True)


def ts(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000).strftime('%m-%d %H:%M')
    except Exception:
        return '?'


def text_of(content):
    if isinstance(content, str):
        return content
    out = []
    for c in content or []:
        if isinstance(c, dict) and c.get('type') == 'text':
            out.append(c.get('text', ''))
    return '\n'.join(out)


# ---- pick targets -----------------------------------------------------------
args = [a for a in sys.argv[1:] if not a.startswith('--')]
take_all = '--all' in sys.argv
files = sorted(f for f in os.listdir(DUMP) if f.endswith('.jsonl'))

targets = []
for fn in files:
    sid = fn[:-6]
    if args:
        if any(sid.startswith(a) for a in args):
            targets.append(sid)
    elif take_all or os.path.getsize(os.path.join(DUMP, fn)) > MIN_MB * 1024 * 1024:
        targets.append(sid)

if not targets:
    print('no targets (raise MIN_MB or pass --all / explicit ids)')
    sys.exit(0)

# ---- extract ----------------------------------------------------------------
for sid in targets:
    p = os.path.join(DUMP, sid + '.jsonl')
    buf, n_u, n_sum = [], 0, 0
    with io.open(p, encoding='utf-8', errors='replace') as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                o = json.loads(raw)
            except Exception:
                continue
            t = o.get('type')
            d = o.get('data') or {}
            if t == 'session/title':
                buf.append(f"\n## TITLE: {d.get('title')}\n")
            elif t == 'goal/change':
                g = d.get('goal') or {}
                buf.append(f"\n**[GOAL {d.get('operation')}]** {g.get('objective')} "
                           f"| phase={g.get('phase')}\n")
            elif t == 'compaction/summary':
                # highest-signal artifact in the whole file: an LLM-written checkpoint
                s = str(d.get('summary') or '')
                n_sum += 1
                buf.append(f"\n### COMPACTION SUMMARY [{ts(o.get('time'))}]\n{s[:SUMM_CAP]}\n")
            elif t == 'user/message':
                # source.kind == 'plugin' is injected runtime context, NOT the human
                if (d.get('source') or {}).get('kind') == 'plugin':
                    continue
                body = text_of(d.get('content')).strip()
                if not body:
                    continue
                n_u += 1
                buf.append(f"\n**[{ts(o.get('time'))}]** {body[:MSG_CAP]}\n")

    out = os.path.join(OUT, sid + '.digest.md')
    with io.open(out, 'w', encoding='utf-8') as g:
        g.write(''.join(buf))
    print(f"{sid}  user_msgs={n_u}  summaries={n_sum}  out={os.path.getsize(out)}B")
