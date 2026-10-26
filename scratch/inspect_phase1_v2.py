import json
import re
from pathlib import Path

backend = Path(r"D:\Projects\SIH26101\SIH26101-Integrated\backend")
api_path = backend / "competency_engine" / "api.py"

print("--- ALL API ROUTES IN API.PY ---")
content = api_path.read_text(encoding="utf-8")
for match in re.finditer(r'@app\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', content):
    print(f"{match.group(1).upper():6} {match.group(2)}")

print("\n--- UPLOADS REGISTRY.JSON ---")
reg_path = backend / "data" / "uploads" / "registry.json"
if reg_path.exists():
    raw = json.loads(reg_path.read_text(encoding="utf-8"))
    print("Keys/Type:", type(raw), list(raw.keys()) if isinstance(raw, dict) else len(raw))
    print(json.dumps(raw, indent=2))

print("\n--- DRAFT QUESTIONS.JSON ---")
drafts_path = backend / "data" / "questions" / "draft_questions.json"
if drafts_path.exists():
    drafts = json.loads(drafts_path.read_text(encoding="utf-8"))
    print(f"Draft count: {len(drafts) if isinstance(drafts, list) else len(drafts.get('drafts', []))}")
    if isinstance(drafts, list) and drafts:
        print("Sample draft keys:", list(drafts[0].keys()))
        print("Sample review_status:", drafts[0].get("review_status"), "id:", drafts[0].get("draft_id"))

print("\n--- QUESTION BANK ---")
qb_path = backend / "data" / "questions" / "question_bank.json"
if qb_path.exists():
    qb = json.loads(qb_path.read_text(encoding="utf-8"))
    questions = qb.get("questions", [])
    print(f"Total questions in bank: {len(questions)}")
    published_from_upload = [q for q in questions if q.get("provenance") == "uploaded_trainer_material" or q.get("source_document_id", "").startswith("SRC-UP-")]
    print(f"Questions published from uploaded material: {len(published_from_upload)}")

print("\n--- EVALUATION SCRIPT ---")
eval_script = backend / "scripts" / "evaluate_question_generation.py"
print(f"evaluate_question_generation.py exists: {eval_script.exists()}")
if eval_script.exists():
    lines = eval_script.read_text(encoding="utf-8").splitlines()
    print("Eval script header/main lines:", len(lines))
    print("\n".join(lines[:25]))
