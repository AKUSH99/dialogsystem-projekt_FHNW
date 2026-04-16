"""
Build data/laptops.db from data/laptops.sql
Run from the project root:  python data/init_db.py
"""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SQL_FILE = ROOT / "laptops.sql"
DB_FILE  = ROOT / "laptops.db"

if DB_FILE.exists():
    DB_FILE.unlink()
    print(f"Removed existing {DB_FILE.name}")

con = sqlite3.connect(DB_FILE)
con.executescript(SQL_FILE.read_text(encoding="utf-8"))
con.commit()

# Quick sanity check
cur = con.execute("SELECT category, COUNT(*) FROM laptops GROUP BY category")
print("\nLaptops loaded:")
for row in cur:
    print(f"  {row[0]:12s} {row[1]:>3} rows")

cur = con.execute("SELECT COUNT(*) FROM laptop_use_cases")
print(f"  use_cases    {cur.fetchone()[0]:>3} rows")

cur = con.execute(
    "SELECT name, price_chf FROM laptops ORDER BY price_chf DESC LIMIT 3"
)
print("\nTop 3 by price:")
for row in cur:
    print(f"  CHF {row[1]:>5}  {row[0]}")

con.close()
print(f"\nDatabase written to {DB_FILE}")
