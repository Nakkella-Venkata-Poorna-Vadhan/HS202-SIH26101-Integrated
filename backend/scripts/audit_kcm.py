"""Independent audit script to verify counts and text fidelity in competencies_kcm.json."""
import json
import csv
import re
from pathlib import Path
import pymupdf

JSON_PATH = Path("data/processed/competencies_kcm.json")
CSV_PATH = Path("data/processed/competencies_kcm.csv")
NOTES_PATH = Path("docs/kcm_extraction_notes.md")
PDF_PATH = Path("data/raw/KCM-Output_RestructuredOct17.pdf")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    jdata = json.load(f)

with open(CSV_PATH, "r", encoding="utf-8") as f:
    cdata = list(csv.DictReader(f))

print(f"JSON records: {len(jdata)}")
print(f"CSV records:  {len(cdata)}")

j_beh_count = sum(1 for r in jdata if r["competency_type"] == "behavioural")
j_func_count = sum(1 for r in jdata if r["competency_type"] == "functional")
print(f"JSON behavioural: {j_beh_count}, functional: {j_func_count}")

total_behaviours_json = sum(len(r["behaviours"]) for r in jdata)
total_behaviours_csv = sum(len(json.loads(r["behaviours"])) for r in cdata)
print(f"Total behaviours in JSON: {total_behaviours_json}")
print(f"Total behaviours in CSV:  {total_behaviours_csv}")

print("\nPer-competency behaviour counts in JSON:")
total = 0
for r in jdata:
    cnt = len(r["behaviours"])
    total += cnt
    print(f"  {r['competency_id']}: {cnt} behaviours - {r['competency_name']}")

print(f"Sum of per-competency counts: {total}")
