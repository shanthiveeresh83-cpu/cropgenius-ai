import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'crop.db')

print(f"📊 Checking database: {db_path}")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print(f"\n✅ Found {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 60)

for table in tables:
    table_name = table[0]
    print(f"\n📋 Table: {table_name}")
    print("-" * 60)

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    print("Columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"\nTotal rows: {count}")

    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        print(f"\nSample data (first {len(rows)} rows):")
        for i, row in enumerate(rows, 1):
            print(f"  Row {i}: {row}")

print("\n" + "=" * 60)
print("✅ Database check complete!")

conn.close()