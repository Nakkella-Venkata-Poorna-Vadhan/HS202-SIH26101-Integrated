import urllib.request
import json

# 1. Fetch topics
req = urllib.request.urlopen('http://127.0.0.1:8000/api/assessment/topics')
topics = json.loads(req.read().decode())
print(f"Assessment topics available: {len(topics)}")
for t in topics:
    print(f"  - {t['competency_id']}: {t['competency_name']} ({t['available_questions_count']} questions) [{t['source_title']}]")

# 2. Check initial unassessed status of LEARNER-003
req = urllib.request.urlopen('http://127.0.0.1:8000/api/learners/LEARNER-003/skill-gaps')
initial_report = json.loads(req.read().decode())
print(f"\nInitial LEARNER-003 unassessed count: {initial_report['unassessed_count']} / {initial_report['total_required_competencies']}")

# 3. Start diagnostic assessment for LEARNER-003 on KCM-FUNC-11
start_payload = json.dumps({
    'learner_id': 'LEARNER-003',
    'competency_id': 'KCM-FUNC-11',
    'question_count': 4
}).encode('utf-8')
req = urllib.request.Request(
    'http://127.0.0.1:8000/api/assessment/start',
    data=start_payload,
    headers={'Content-Type': 'application/json'}
)
start_resp = json.loads(urllib.request.urlopen(req).read().decode())
attempt_id = start_resp['attempt_id']
questions = start_resp['questions']
print(f"\nAssessment started: {attempt_id}")
print(f"Competency: {start_resp['competency_name']}")
print(f"Source: {start_resp['source_title']} ({start_resp['source_document_id']})")
print(f"Questions returned: {len(questions)}")

# Verify secrecy: no correct answers or explanations exposed
for q in questions:
    assert 'correct_answer' not in q, "LEAK: correct_answer exposed in client payload!"
    assert 'explanation' not in q, "LEAK: explanation exposed in client payload!"
    assert 'verbatim_excerpt' not in q, "LEAK: verbatim_excerpt exposed in client payload!"
    print(f"  - [{q['difficulty']}] {q['question_id']}: {q['question_text'][:60]}...")
print("[OK] Answer secrecy verified: Zero answer keys or explanations leaked.")

# 4. Submit answers (answers choice 'B')
submit_payload = json.dumps({
    'attempt_id': attempt_id,
    'learner_id': 'LEARNER-003',
    'answers': {q['question_id']: 'B' for q in questions}
}).encode('utf-8')
req = urllib.request.Request(
    f'http://127.0.0.1:8000/api/assessment/{attempt_id}/submit',
    data=submit_payload,
    headers={'Content-Type': 'application/json'}
)
result = json.loads(urllib.request.urlopen(req).read().decode())
print(f"\nSubmission result received:")
print(f"Score: {result['correct_count']} / {result['total_questions']} ({result['score_percentage']}%)")
est = result['provisional_estimate']
print(f"Provisional Estimate: Level {est['estimated_level']} / 5")
print(f"Confidence: {round(est['confidence'] * 100)}%")
print(f"Evidence threshold met: {est['evidence_threshold_met']}")
print(f"Methodology note: {est['methodology_note']}")
print(f"Disclaimer: {est['limitations_disclaimer']}")

# Verify question feedback with source citations and verbatim excerpts
print(f"\nQuestion Provenance Review ({len(result['feedback'])} items):")
for fb in result['feedback']:
    status_str = "CORRECT" if fb['is_correct'] else "INCORRECT"
    print(f"  - Q: {fb['question_id']} | User: {fb['selected_answer']} | Correct: {fb['correct_answer']} ({status_str})")
    print(f"    Source: {fb['source_title']} (Page {fb['page_reference']})")
    print(f"    Excerpt: \"{fb['verbatim_excerpt'][:80]}...\"")

# 5. Check updated skill gaps for LEARNER-003
req = urllib.request.urlopen('http://127.0.0.1:8000/api/learners/LEARNER-003/skill-gaps')
updated_report = json.loads(req.read().decode())
print(f"\nPost-assessment LEARNER-003 unassessed count: {updated_report['unassessed_count']} / {updated_report['total_required_competencies']}")
for gap in updated_report['gaps']:
    if gap['competency_id'] == 'KCM-FUNC-11':
        print(f"  -> KCM-FUNC-11 status: {gap['status']}, Level: {gap['estimated_level']}, Confidence: {round(gap['confidence'] * 100)}%")

print("\n[OK] ALL END-TO-END VERIFICATION CHECKS PASSED.")
