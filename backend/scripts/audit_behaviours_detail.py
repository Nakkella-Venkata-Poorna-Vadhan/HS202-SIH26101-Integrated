"""Audit all 118 behaviours in competencies_kcm.json."""
import json

with open("data/processed/competencies_kcm.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data:
    cid = r["competency_id"]
    name = r["competency_name"]
    behs = r["behaviours"]
    print(f"\n=== [{cid}] {name} (Count: {len(behs)}, Pages: {r['source_page']}) ===")
    for idx, b in enumerate(behs, 1):
        # print first 100 chars
        print(f"  {idx}. {b[:100]!r}")
