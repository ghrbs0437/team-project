"""user 1~297 을 10명씩 끊어서 추출 (one-shot 드라이버)."""
from __future__ import annotations
import sys
import time
import traceback

sys.stdout.reconfigure(encoding="utf-8")

from app.ontology.util.extract_ontology import extract_user

START, END, CHUNK = 1, 297, 10
t0_global = time.time()
ok = 0
fail = 0
fails = []

for chunk_start in range(START, END + 1, CHUNK):
    chunk_end = min(chunk_start + CHUNK - 1, END)
    chunk_no = (chunk_start - 1) // CHUNK + 1
    print(f"\n=== chunk {chunk_no:02d}: users {chunk_start}-{chunk_end} ===", flush=True)
    t_chunk = time.time()
    chunk_relations = 0
    for uid in range(chunk_start, chunk_end + 1):
        t0 = time.time()
        try:
            _, r = extract_user(uid)
            ok += 1
            chunk_relations += r
            print(f"  user_{uid:<3} relations={r:<3}  ({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            fail += 1
            fails.append((uid, str(e)))
            print(f"  user_{uid:<3} FAILED: {e}", flush=True)
    elapsed = time.time() - t_chunk
    print(
        f"--- chunk {chunk_no:02d} done: relations+{chunk_relations}, "
        f"{elapsed:.1f}s, cumulative ok={ok}/fail={fail} ---",
        flush=True,
    )

print(f"\n========== ALL DONE: total {time.time()-t0_global:.0f}s, ok={ok}, fail={fail} ==========")
if fails:
    print("Failed users:")
    for uid, msg in fails:
        print(f"  user_{uid}: {msg}")
