# Invoice Audit Agent

An AI agent that checks incoming invoices against purchase orders on file and decides **Approve / Flag / Reject** — with a clear, human-readable reason for every decision.

Built to mirror a real accounts-payable workflow: catching price overcharges, duplicate billing, and unverifiable invoices before they get paid, instead of relying on manual review.

## Why this exists

Every company that pays vendors deals with this problem. Someone on the finance team manually checks invoices against purchase orders, and mistakes (or fraud) slip through when volume gets high. This project explores how far an LLM-based agent can go in automating that first pass — flagging what needs a human, and clearing what doesn't.

## How it works

```
Invoice comes in
      │
      ▼
Duplicate check (plain code, no LLM — fast and free)
      │
      ▼
Look up matching Purchase Order in database (SQL, no LLM)
      │
      ▼
Claude compares invoice vs. PO and judges: APPROVE / FLAG / REJECT
(this is the one LLM call — reasoning happens here)
      │
      ▼
Decision + reason saved to database
```

The design is deliberate: deterministic steps (duplicate detection, database lookups) run as plain code because they're fast, free, and 100% predictable. The LLM is only used for the step that actually needs judgment — comparing two records and deciding whether a discrepancy is a mistake, fraud, or a false alarm.

## Proof it works, not just a demo

Most AI demos show a few cherry-picked examples. This project includes a separate **evaluation harness** — a set of invoices with known-correct answers, scored automatically against the agent's real output.

**Result on first full run: 15/16 correct (93.8% accuracy).**

The one disagreement was genuinely instructive: the agent flagged an invoice with a slightly different vendor name for human review rather than auto-rejecting it, reasoning that a name variation could be a legitimate rebrand rather than fraud, since every other field matched exactly. That's arguably the safer real-world call — a reminder that "correct" isn't always a fixed answer key, and eval design has to account for that.

## Tech stack

- **Python** — core logic
- **Anthropic Claude API** — the judgment/reasoning step
- **SQLite** — purchase order database and audit results storage
- **JSON** — invoice data interchange

## Project structure

```
invoice-audit-agent/
├── setup_db.py          # Creates the purchase order database
├── generate_invoices.py # Generates test invoices (clean + intentionally flawed)
├── agent.py              # The agent — LLM connects here
├── eval.py                # Scores the agent's decisions against known-correct answers
└── README.md
```

## Running it locally

```bash
pip install anthropic
export ANTHROPIC_API_KEY=your-key-here   # Windows PowerShell: $env:ANTHROPIC_API_KEY="your-key-here"

python setup_db.py
python generate_invoices.py
python agent.py
python eval.py
```

## What I'd build next

- Move the LLM calls to AWS Bedrock and deploy the pipeline on EC2
- Add a Streamlit dashboard for live, non-technical demos
- Extend the pipeline with a vision step, so Claude reads scanned invoice images directly instead of structured JSON input
- Swap the exact-match PO lookup for a retrieval-based (RAG) approach to handle less structured incoming data

## What this project is really about

Beyond the invoice use case, this is a small, complete example of the core pattern behind most real-world enterprise AI systems: know exactly where deterministic logic ends and LLM judgment begins, and don't ship an AI system without a way to measure whether it's actually right.
