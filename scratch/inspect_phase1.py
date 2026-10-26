import re
from pathlib import Path

backend = Path(r"D:\Projects\SIH26101\SIH26101-Integrated\backend")
api_path = backend / "competency_engine" / "api.py"

print("--- API ROUTES ---")
lines = api_path.read_text(encoding="utf-8").splitlines()
for line in lines:
    m = re.match(r"@app\.(get|post|put|delete|patch)\(([^)]+)\)", line.strip())
    if m:
        print(f"{m.group(1).upper():6} {m.group(2)}")

print("\n--- TEST FILES IN BACKEND ---")
test_dir = backend / "tests"
for tf in sorted(test_dir.glob("test_*.py")):
    print(f"{tf.name}")

print("\n--- UPLOADS REGISTRY ---")
reg_path = backend / "data" / "uploads" / "registry.json"
if reg_path.exists():
    print(f"Registry exists, size: {len(reg_path.read_text(encoding='utf-8'))} bytes")
    import json
    data = json.loads(reg_path.read_text(encoding="utf-8"))
    print(f"Uploaded documents: {len(data)}")
    for d in data:
        print(f"  - {d.get('document_id')}: {d.get('filename')} (status: {d.get('status')})")

print("\n--- QUESTION BANK STATS ---")
qb_path = backend / "data" / "questions" / "question_bank.json"
drafts_path = backend / "data" / "questions" / "draft_questions.json"
if qb_path.exists():
    import json
    qb = json.loads(qb_path.read_text(encoding="utf-8"))
    print(f"Questions in bank: {len(qb.get('questions', []))}")
    sources = set(q.get("source_document_id") for q in qb.get("questions", []))
    print(f"  Source document IDs in bank: {sources}")
if drafts_path.exists():
    import json
    drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
    print(f"Draft questions: {len(drafts)}")
    statuses = {}
    for d in drafts:
        s = d.get("review_status")
        statuses[s] = statuses.get(s, 0) + 1
    print(f"  Draft statuses: {statuses}")
