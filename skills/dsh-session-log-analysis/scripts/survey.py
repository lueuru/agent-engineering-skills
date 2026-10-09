# -*- coding: utf-8 -*-
"""盘点 DSH 会话日志：解压 -> 统计 -> 输出摘要

Usage:
    python survey.py [SESSIONS_DIR] > _session_survey.json

Env:
    OUT  解压输出目录 (default: ./_session_dump)
"""
import zstandard, json, os, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 \
    else os.environ.get('SESSIONS_DIR', r'C:\Users\Administrator\Desktop\sessions')
OUT = os.environ.get('OUT', r'C:\Users\Administrator\Desktop\_session_dump')
os.makedirs(OUT, exist_ok=True)

results = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    for fn in filenames:
        if not fn.endswith('.zstd'):
            continue
        path = os.path.join(dirpath, fn)
        sid = os.path.basename(dirpath)
        proj = os.path.relpath(dirpath, ROOT).split(os.sep)[0]
        try:
            with open(path, 'rb') as f:
                data = zstandard.ZstdDecompressor().stream_reader(f).read()
            text = data.decode('utf-8', errors='replace')
        except Exception as e:
            results.append({'proj': proj, 'sid': sid, 'err': str(e)})
            continue
        lines = [l for l in text.split('\n') if l.strip()]
        # dump
        with open(os.path.join(OUT, sid + '.jsonl'), 'w', encoding='utf-8') as g:
            g.write(text)
        types = {}
        head = None
        first_user = []
        last_ts = None
        cost = 0.0
        for l in lines:
            try:
                o = json.loads(l)
            except Exception:
                continue
            t = o.get('type', '?')
            types[t] = types.get(t, 0) + 1
            if head is None:
                head = o
            ts = o.get('timestamp') or o.get('createdAt')
            if ts:
                last_ts = ts
            if t == 'user':
                c = o.get('content')
                if isinstance(c, list):
                    c = ' '.join(x.get('text', '') for x in c if isinstance(x, dict))
                if isinstance(c, str):
                    first_user.append(c[:300])
            u = o.get('usage') or {}
            if isinstance(u, dict):
                cost += float(u.get('totalCost') or 0)
        results.append({
            'proj': proj, 'sid': sid,
            'size': os.path.getsize(path),
            'lines': len(lines),
            'types': types,
            'cwd': (head or {}).get('cwd'),
            'created': (head or {}).get('createdAt'),
            'last_ts': last_ts,
            'cost': round(cost, 4),
            'n_user': len(first_user),
            'first_user': first_user[:3],
        })

results.sort(key=lambda r: (r.get('created') or ''))
print(json.dumps(results, ensure_ascii=False, indent=2))
