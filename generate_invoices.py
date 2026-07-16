"""
STEP 2: Generate fake incoming invoices to test the auditor on.
We're keeping these as plain JSON (not PDFs/images) so you can build
and understand the core agent first. Reading real scanned PDFs is a
week-2 upgrade, not day-1 complexity.
Run this once: python generate_invoices.py
"""
import json

invoices = [
    # --- Clean matches (should APPROVE) ---
    {"invoice_id": "INV-001", "po_number": "PO-1001", "vendor": "Acme Office Supplies",
     "item": "A4 Paper (box)", "quantity": 50, "unit_price": 12.50},
    {"invoice_id": "INV-002", "po_number": "PO-1003", "vendor": "BrightTech Hardware",
     "item": "USB-C Cable", "quantity": 100, "unit_price": 3.20},
    {"invoice_id": "INV-003", "po_number": "PO-1007", "vendor": "GreenLeaf Catering",
     "item": "Lunch Catering (event)", "quantity": 1, "unit_price": 1500.00},
    {"invoice_id": "INV-004", "po_number": "PO-1010", "vendor": "BrightTech Hardware",
     "item": "Wireless Mouse", "quantity": 40, "unit_price": 15.00},
    {"invoice_id": "INV-005", "po_number": "PO-1013", "vendor": "Nova Cleaning Co",
     "item": "Carpet Deep Clean", "quantity": 1, "unit_price": 400.00},

    # --- Price overcharges (should FLAG) ---
    {"invoice_id": "INV-006", "po_number": "PO-1002", "vendor": "Acme Office Supplies",
     "item": "Toner Cartridge", "quantity": 10, "unit_price": 62.00},  # PO says 45.00
    {"invoice_id": "INV-007", "po_number": "PO-1005", "vendor": "Skyline Logistics",
     "item": "Freight - Pallet", "quantity": 5, "unit_price": 310.00},  # PO says 220.00
    {"invoice_id": "INV-008", "po_number": "PO-1014", "vendor": "BrightTech Hardware",
     "item": "Monitor 27in", "quantity": 15, "unit_price": 245.00},  # PO says 180.00

    # --- Quantity mismatch (should FLAG) ---
    {"invoice_id": "INV-009", "po_number": "PO-1004", "vendor": "BrightTech Hardware",
     "item": "Laptop Stand", "quantity": 35, "unit_price": 28.00},  # PO says qty 20

    # --- Vendor mismatch — invoice claims different vendor than PO on file (should REJECT) ---
    {"invoice_id": "INV-010", "po_number": "PO-1006", "vendor": "Skyline Freight Partners",
     "item": "Warehouse Storage (month)", "quantity": 1, "unit_price": 800.00},

    # --- Duplicate invoice (same invoice ID/PO billed twice — should REJECT second one) ---
    {"invoice_id": "INV-011", "po_number": "PO-1009", "vendor": "Acme Office Supplies",
     "item": "Whiteboard Markers (pack)", "quantity": 30, "unit_price": 8.75},
    {"invoice_id": "INV-011", "po_number": "PO-1009", "vendor": "Acme Office Supplies",
     "item": "Whiteboard Markers (pack)", "quantity": 30, "unit_price": 8.75},  # duplicate!

    # --- PO number doesn't exist at all (should REJECT) ---
    {"invoice_id": "INV-012", "po_number": "PO-9999", "vendor": "Unknown Vendor LLC",
     "item": "Consulting Services", "quantity": 1, "unit_price": 5000.00},

    # --- Small, easily-missed overcharge (tests if the agent catches subtle stuff) ---
    {"invoice_id": "INV-013", "po_number": "PO-1015", "vendor": "Acme Office Supplies",
     "item": "Sticky Notes (pack)", "quantity": 60, "unit_price": 4.95},  # PO says 4.25

    # --- Clean ones again, to balance the set ---
    {"invoice_id": "INV-014", "po_number": "PO-1008", "vendor": "Nova Cleaning Co",
     "item": "Office Cleaning (month)", "quantity": 1, "unit_price": 950.00},
    {"invoice_id": "INV-015", "po_number": "PO-1012", "vendor": "GreenLeaf Catering",
     "item": "Coffee Service (month)", "quantity": 1, "unit_price": 300.00},
]

with open("invoices.json", "w") as f:
    json.dump(invoices, f, indent=2)

print(f"✅ Generated {len(invoices)} invoices into invoices.json")
