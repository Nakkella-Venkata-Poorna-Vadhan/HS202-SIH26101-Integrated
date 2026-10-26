import json

with open("data/processed/competencies_kcm.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for r in data[:13]:
    cid = r["competency_id"]
    name = r["competency_name"]
    behs = r["behaviours"]
    print(f"\n=== [{cid}] {name} (Count: {len(behs)}, Pages: {r['source_page']}) ===")
    for idx, b in enumerate(behs, 1):
        print(f"  {idx}. {b[:100]!r}")
