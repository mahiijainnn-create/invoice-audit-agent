"""
STEP 4: The eval harness. This is the single most important file
for your interview story — it's what separates "I built a demo" from
"I can prove this works." No LLM call here, just scoring.

Run AFTER agent.py: python eval.py
"""
import sqlite3

# The ground truth — what SHOULD have happened for each invoice.
# We know this because we designed the invoices ourselves.
expected = {
    "INV-001": "APPROVE", "INV-002": "APPROVE", "INV-003": "APPROVE",
    "INV-004": "APPROVE", "INV-005": "APPROVE",
    "INV-006": "FLAG", "INV-007": "FLAG", "INV-008": "FLAG", "INV-009": "FLAG",
    "INV-013": "FLAG",
    "INV-010": "REJECT", "INV-012": "REJECT",
    # INV-011 appears twice: first is APPROVE, second (duplicate) is REJECT.
    # We handle that case separately below since dict keys can't repeat.
    "INV-014": "APPROVE", "INV-015": "APPROVE",
}

conn = sqlite3.connect("company.db")
cur = conn.cursor()
cur.execute("SELECT invoice_id, decision, reason FROM audit_results")
rows = cur.fetchall()

correct = 0
total = 0
mistakes = []

# Track INV-011 occurrence order to check first=APPROVE, second=REJECT
inv011_seen = 0

for invoice_id, decision, reason in rows:
    if invoice_id == "INV-011":
        inv011_seen += 1
        expected_decision = "APPROVE" if inv011_seen == 1 else "REJECT"
    else:
        expected_decision = expected.get(invoice_id)

    if expected_decision is None:
        continue

    total += 1
    if decision == expected_decision:
        correct += 1
    else:
        mistakes.append((invoice_id, expected_decision, decision, reason))

accuracy = (correct / total * 100) if total else 0

print(f"\n{'='*50}")
print(f"EVAL RESULTS: {correct}/{total} correct ({accuracy:.1f}% accuracy)")
print(f"{'='*50}")

if mistakes:
    print("\nMistakes:")
    for invoice_id, expected_decision, got_decision, reason in mistakes:
        print(f"  {invoice_id}: expected {expected_decision}, got {got_decision}")
        print(f"     agent's reason: {reason}")
else:
    print("\nNo mistakes — agent matched expected decisions on every case.")

print(f"\n{'='*50}")
