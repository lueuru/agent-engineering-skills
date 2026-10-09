# -*- coding: utf-8 -*-
"""把 DSH 会话 JSONL 还原成可读转录 (Tier A)

Usage:
    ASSIST_LIMIT=1500 python extract.py

Env:
    DUMP           *.jsonl 输入目录      (default: ./_session_dump)
    OUT            *.md 输出目录         (default: ./_session_transcripts)
    ASSIST_LIMIT   每条 assistant 消息截断 (default 1200)
    TOOLARG_LIMIT  每个 tool-call 参数截断 (default 220)
"""
import json, os, io, sys, datetime

DUMP = os.environ.get('DUMP', r'C:\Users\Administrator\Desktop\_session_dump')
OUT = os.environ.get('OUT', r'C:\Users\Administrator\Desktop\_session_transcripts')
os.makedirs(OUT, exist_ok=True)

ASSIST_LIMIT = int(os.environ.get('ASSIST_LIMIT', '1200'))
TOOLARG_LIMIT = int(os.environ.get('TOOLARG_LIMIT', '220'))


def ts(ms):
    try:
        return datetime.datetime.fromtimestamp(ms / 1000).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return '?'


def text_of(content):
    out = []
    if isinstance(content, str):
        return content
    for c in content or []:
        if not isinstance(c, dict):
            continue
        if c.get('type') == 'text':
            out.append(c.get('text', ''))
    return '\n'.join(out)


for fn in sorted(os.listdir(DUMP)):
    if not fn.endswith('.jsonl'):
        continue
    path = os.path.join(DUMP, fn)
    sid = fn[:-6]
    lines_out = []
    title = None
    head = None
    n_tool = {}
    with io.open(path, encoding='utf-8', errors='replace') as f:
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
            if t == 'session':
                head = o
                lines_out.append(f"# Session {o.get('id')}\n")
                lines_out.append(f"- cwd: `{o.get('cwd')}`\n")
                lines_out.append(f"- createdAt: {ts(o.get('createdAt'))}\n")
            elif t == 'session/title':
                tt = d.get('title')
                if tt and not title:
                    title = tt
                    lines_out.append(f"- title: **{tt}**\n")
            elif t == 'goal/change':
                g = d.get('goal') or {}
                lines_out.append(f"\n> **[GOAL {d.get('operation')}]** {g.get('objective')} (phase={g.get('phase')})\n")
            elif t == 'compaction/summary':
                s = d.get('summary') or d.get('text') or json.dumps(d, ensure_ascii=False)
                lines_out.append(f"\n> **[COMPACT SUMMARY]**\n> {str(s)[:4000]}\n")
            elif t == 'user/message':
                src = (d.get('source') or {}).get('kind')
                body = text_of(d.get('content')).strip()
                if not body:
                    continue
                lines_out.append(f"\n### 👤 USER ({src}) [{ts(o.get('time'))}]\n{body}\n")
            elif t == 'assistant/message':
                m = d.get('message') or {}
                body = text_of(m.get('content')).strip()
                if not body:
                    continue
                if len(body) > ASSIST_LIMIT:
                    body = body[:ASSIST_LIMIT] + f"\n...(截断, 共{len(body)}字)"
                lines_out.append(f"\n**🤖 ASSISTANT [{ts(o.get('time'))}]**\n{body}\n")
            elif t == 'tool/call':
                name = d.get('name')
                n_tool[name] = n_tool.get(name, 0) + 1
                args = d.get('arguments') or ''
                if len(args) > TOOLARG_LIMIT:
                    args = args[:TOOLARG_LIMIT] + '…'
                lines_out.append(f"- 🔧 `{name}` {args}")
            elif t == 'tool/result':
                m = d.get('message') or {}
                txt = ''
                for c in m.get('content') or []:
                    for cc in (c.get('content') or []):
                        if isinstance(cc, dict) and cc.get('type') == 'text':
                            txt += cc.get('text', '')
                if m.get('isError') or 'isError' in json.dumps(m)[:200]:
                    pass
                if len(txt) > 400:
                    txt = txt[:400] + '…'
                lines_out.append(f"  ↳ {txt.replace(chr(10), ' | ')}")

    with io.open(os.path.join(OUT, sid + '.md'), 'w', encoding='utf-8') as g:
        g.write(''.join(lines_out))

    print(f"{sid}  title={title}  tools={n_tool}  out={os.path.getsize(os.path.join(OUT, sid + '.md'))}")
