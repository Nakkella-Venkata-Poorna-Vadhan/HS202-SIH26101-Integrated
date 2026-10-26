"""Comprehensive audit comparing extracted JSON against raw PDF for all 34 competencies."""
import json
import pymupdf
from pathlib import Path

PDF_PATH = Path("data/raw/KCM-Output_RestructuredOct17.pdf")
JSON_PATH = Path("data/processed/competencies_kcm.json")

doc = pymupdf.open(str(PDF_PATH))
with open(JSON_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)

print(f"Loaded {len(records)} records from JSON.")

# Official sub-themes according to KCM document (from summary pages & annexures)
OFFICIAL_KCM_SUBTHEMES = {
    "KCM-BEH-01": ["Self-Learning", "Self-Analysis", "Self Confidence", "Purposefulness"],
    "KCM-BEH-02": ["Stress Management", "Navigating Ambiguity", "Resilience"],
    "KCM-BEH-03": ["Attention to Detail", "Systems Thinking", "Analytical Thinking"],
    "KCM-BEH-04": ["Reading & Comprehension", "Active Listening", "Verbal & Non-verbal communication", "Presentation skills"],
    "KCM-BEH-05": ["Initiative & Drive", "Goal Setting", "Accountability", "Commitment to Quality"],
    "KCM-BEH-06": ["Relationship Management", "Knowledge Sharing", "Diversity & Inclusion"],
    "KCM-BEH-07": ["Empathy", "Responsiveness", "Service Excellence (wrt Citizens)"],
    "KCM-BEH-08": ["Process Excellence", "Resource Management", "Continuous Improvement", "Planning & Prioritization"],
    "KCM-BEH-09": ["Lateral Thinking", "Transformation Orientation"],
    "KCM-BEH-10": ["Global Mindset", "Forward Thinking", "Executive Presence", "Sustainable Mindset"],
    "KCM-BEH-11": ["Influencing & Negotiation", "Conflict Management"],
    "KCM-BEH-12": ["Mentoring", "Inspiring Others", "Sharing Constructive Feedback"],
    "KCM-BEH-13": ["Logical Reasoning", "Sound Judgement"],
    "KCM-FUNC-01": ["Design Thinking", "Citizen Partnering & Collaboration", "Political, Economic, Social, Technological Consciousness"],
    "KCM-FUNC-02": ["Research & Needs Analysis", "Policy Design /Amendment", "Policy Implementation", "Policy Monitoring & Impact Assessment"],
    "KCM-FUNC-03": ["Rules of Business", "Cabinet Note Writing"],
    "KCM-FUNC-04": ["Research & Needs Analysis", "Scheme / Program Design", "Feasibility and Risk Assessment", "Implementation & Outreach"],
    "KCM-FUNC-05": ["Project Planning", "Project Implementation", "Project Evaluation", "Project KPIs Monitoring"],
    "KCM-FUNC-06": ["Procurement management through GeM", "Procurement of Goods / Services / Works", "Contract Management", "Vendor / Consultant Management"],
    "KCM-FUNC-07": ["Inventory Management", "Maintenance and Disposal of materials"],
    "KCM-FUNC-08": ["Creation of M&E Framework", "Evaluation and output / outcome"],
    "KCM-FUNC-09": ["Budget Formulation & Implementation", "PFMS Portal Management", "Expenditure Management", "Government Accounts"],
    "KCM-FUNC-10": ["Digital Tools (MS office, Excel & PPT) and Platforms", "Digital Service Design"],
    "KCM-FUNC-11": ["Data Management (Clean-up, segregation, processing)", "Data Analysis & Visualization", "Data-led Decision Making", "Data Use & Governance"],
    "KCM-FUNC-12": ["Establishment Matters", "Fundamental Rules / Supplementary Rules (FRSR)", "Reservations", "Prevention of Sexual Harassment Policy", "Performance Appraisal"],
    "KCM-FUNC-13": ["E-Office", "File/DAK Management", "Office Procedures", "Noting & Drafting of official Communications", "Technical Proposal / Report writing"],
    "KCM-FUNC-14": ["Submission of briefs, supply of information", "Maintaining records of parliamentary matters"],
    "KCM-FUNC-15": ["RTI Responsiveness", "RTI Records and Report management"],
    "KCM-FUNC-16": ["Manage cases on CPGRAMS", "Public Grievance Handling"],
    "KCM-FUNC-17": ["Conduct Rules", "Provisions on Suspension", "Proposal preparation for disciplinary proceedings", "Handling prosecution cases; supporting investigations", "Preventive Vigilance"],
    "KCM-FUNC-18": ["Legal Know-how: Basic Knowledge of Legal drafting", "Court Cases Management", "LIMBS Portal Management"],
    "KCM-FUNC-19": ["Dissemination of Information", "Handling social media (engagement)", "Management of information on official websites"],
    "KCM-FUNC-20": ["Change Readiness", "Accepting Change", "Implementing Change"],
    "KCM-FUNC-21": ["Allowances & Reimbursements", "Leave and Travel", "Miscellaneous matters (Telephone, Car, Residence, Personal Staff etc.)", "Implementing Official Language"],
}

print("\n=== AUDIT RESULTS BY COMPETENCY ===")
total_official_subthemes = 0
for cid, expected_subthemes in OFFICIAL_KCM_SUBTHEMES.items():
    total_official_subthemes += len(expected_subthemes)

print(f"Total Official KCM Sub-Themes in Reference List: {total_official_subthemes}")

mismatches = []
for r in records:
    cid = r["competency_id"]
    name = r["competency_name"]
    behs = r["behaviours"]
    expected = OFFICIAL_KCM_SUBTHEMES.get(cid, [])
    
    # Check count
    count_mismatch = len(behs) != len(expected)
    
    # Check if extracted behaviours have corrupted titles (like ':' in weird places or combined titles)
    corrupted_titles = []
    for b in behs:
        # Check if first part before colon looks like a real sub-theme
        if ":" in b:
            t = b.split(":")[0].strip()
            # If t is very long (contains multiple subthemes or is a sentence fragment)
            if len(t) > 50 or " " in t and any(word in t for word in ["Demonstrates", "Displays", "Exhibits", "Ability"]):
                corrupted_titles.append(t)
        else:
            corrupted_titles.append("NO_COLON: " + b[:40])
            
    if count_mismatch or corrupted_titles:
        mismatches.append({
            "id": cid,
            "name": name,
            "pages": r["source_page"],
            "extracted_count": len(behs),
            "official_count": len(expected),
            "expected_subthemes": expected,
            "corrupted_titles": corrupted_titles,
            "extracted_behaviours": behs,
        })

print(f"\nTotal Competencies with count or title mismatches: {len(mismatches)} out of 34!")
for m in mismatches:
    print(f"\n[{m['id']}] {m['name']} (Pages {m['pages']}):")
    print(f"  Official count: {m['official_count']} | Extracted count: {m['extracted_count']}")
    print(f"  Official subthemes: {m['expected_subthemes']}")
    print(f"  Corrupted/Malformed entries detected: {len(m['corrupted_titles'])}")
    for ct in m['corrupted_titles']:
        print(f"    - {ct}")

doc.close()
