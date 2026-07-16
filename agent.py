"""
STEP 3: The actual agent. This is where the LLM gets called.

Flow per invoice:
  1. Look up the matching PO in SQLite         <- plain code, no LLM
  2. Check for exact-duplicate invoice IDs      <- plain code, no LLM
  3. Send invoice + PO to Claude, ask it to     <- THIS IS THE LLM CALL
     decide APPROVE / FLAG / REJECT with a reason
  4. Save the decision back to SQLite

Run: python agent.py
Requires: pip install anthropic
Requires: an environment variable ANTHROPIC_API_KEY set to your key
"""
import json
import os
import sqlite3

import anthropic

client = anthropic.Anthropic(
   default_headers={"anthropic-workspace-id": os.environ["ANTHROPIC_WORKSPACE_ID"]},
) # reads ANTHROPIC_API_KEY from your environment automatically

conn = sqlite3.connect("company.db")
cur = conn.cursor()

# Table to store the agent's decisions
cur.execute("DROP TABLE IF EXISTS audit_results")
cur.execute("""
CREATE TABLE audit_results (
    invoice_id TEXT,
    decision TEXT,
    reason TEXT,
    confidence TEXT
)
""")
conn.commit()


def get_po(po_number):
    """Plain SQL lookup. No LLM involved — this is deterministic."""
    cur.execute("SELECT po_number, vendor, item, quantity, unit_price FROM purchase_orders WHERE po_number = ?", (po_number,))
    row = cur.fetchone()
    if row is None:
        return None
    return {"po_number": row[0], "vendor": row[1], "item": row[2], "quantity": row[3], "unit_price": row[4]}


def is_duplicate(invoice_id, seen_ids):
    """Plain code check. No LLM needed for exact-match duplicate detection."""
    return invoice_id in seen_ids


def ask_llm_to_judge(invoice, po):
    """
    THE LLM CALL. We hand Claude the invoice and the PO (or tell it
    there's no matching PO) and ask it to reason about whether this
    should be approved, flagged, or rejected — and explain why.
    """
    prompt = f"""You are an accounts-payable auditor. Compare this invoice to the purchase order on file and decide.

INVOICE:
{json.dumps(invoice, indent=2)}

PURCHASE ORDER ON FILE:
{json.dumps(po, indent=2) if po else "NO MATCHING PURCHASE ORDER FOUND IN SYSTEM"}

Rules:
- APPROVE if vendor, item, quantity, and price all match (small rounding is fine).
- FLAG if there's a price increase, quantity mismatch, or vendor name is slightly different — something a human should double check, but it might be legitimate.
- REJECT if there is no matching PO, the vendor is completely different, or this looks fraudulent.

Respond with ONLY valid JSON, no other text:
{{"decision": "APPROVE|FLAG|REJECT", "reason": "one sentence, be specific with numbers", "confidence": "HIGH|MEDIUM|LOW"}}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_text = response.content[0].text.strip()
    # Claude sometimes wraps JSON in ```json fences — strip those if present
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return {"decision": "FLAG", "reason": f"Could not parse LLM response: {raw_text}", "confidence": "LOW"}


def run_audit():
    with open("invoices.json") as f:
        invoices = json.load(f)

    seen_ids = set()

    for invoice in invoices:
        invoice_id = invoice["invoice_id"]
        print(f"\n--- Processing {invoice_id} ---")

        # Deterministic check #1: exact duplicate invoice ID
        if is_duplicate(invoice_id, seen_ids):
            decision = {"decision": "REJECT", "reason": f"Duplicate invoice ID {invoice_id} already processed.", "confidence": "HIGH"}
            print(f"  -> {decision['decision']} (duplicate, caught by code, no LLM needed): {decision['reason']}")
        else:
            seen_ids.add(invoice_id)
            po = get_po(invoice["po_number"])
            print(f"  Looked up {invoice['po_number']}: {'found' if po else 'NOT FOUND'}")

            # LLM call happens here
            decision = ask_llm_to_judge(invoice, po)
            print(f"  -> {decision['decision']} ({decision['confidence']} confidence): {decision['reason']}")

        cur.execute(
            "INSERT INTO audit_results VALUES (?, ?, ?, ?)",
            (invoice_id, decision["decision"], decision["reason"], decision["confidence"])
        )
        conn.commit()

    print("\n✅ Audit complete. Results saved to company.db -> audit_results table.")


if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  Set your API key first: export ANTHROPIC_API_KEY=sk-ant-...")
    else:
        run_audit()
