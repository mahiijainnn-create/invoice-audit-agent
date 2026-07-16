"""
STEP 1: Create the company's Purchase Order database.
This is the "source of truth" — what invoices SHOULD match.
Run this once: python setup_db.py
"""
import sqlite3

conn = sqlite3.connect("company.db")
cur = conn.cursor()

# Start fresh each time we run this
cur.execute("DROP TABLE IF EXISTS purchase_orders")
cur.execute("""
CREATE TABLE purchase_orders (
    po_number TEXT PRIMARY KEY,
    vendor TEXT,
    item TEXT,
    quantity INTEGER,
    unit_price REAL
)
""")

# 15 fake but realistic purchase orders
purchase_orders = [
    ("PO-1001", "Acme Office Supplies", "A4 Paper (box)", 50, 12.50),
    ("PO-1002", "Acme Office Supplies", "Toner Cartridge", 10, 45.00),
    ("PO-1003", "BrightTech Hardware", "USB-C Cable", 100, 3.20),
    ("PO-1004", "BrightTech Hardware", "Laptop Stand", 20, 28.00),
    ("PO-1005", "Skyline Logistics", "Freight - Pallet", 5, 220.00),
    ("PO-1006", "Skyline Logistics", "Warehouse Storage (month)", 1, 800.00),
    ("PO-1007", "GreenLeaf Catering", "Lunch Catering (event)", 1, 1500.00),
    ("PO-1008", "Nova Cleaning Co", "Office Cleaning (month)", 1, 950.00),
    ("PO-1009", "Acme Office Supplies", "Whiteboard Markers (pack)", 30, 8.75),
    ("PO-1010", "BrightTech Hardware", "Wireless Mouse", 40, 15.00),
    ("PO-1011", "Skyline Logistics", "Freight - Container", 2, 3400.00),
    ("PO-1012", "GreenLeaf Catering", "Coffee Service (month)", 1, 300.00),
    ("PO-1013", "Nova Cleaning Co", "Carpet Deep Clean", 1, 400.00),
    ("PO-1014", "BrightTech Hardware", "Monitor 27in", 15, 180.00),
    ("PO-1015", "Acme Office Supplies", "Sticky Notes (pack)", 60, 4.25),
]

cur.executemany(
    "INSERT INTO purchase_orders VALUES (?, ?, ?, ?, ?)", purchase_orders
)
conn.commit()
conn.close()

print(f"✅ Created company.db with {len(purchase_orders)} purchase orders.")
