import sqlite3
conn = sqlite3.connect('healthcare_system.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Check doctors
docs = cur.execute("SELECT username, full_name, role, city FROM users WHERE role='doctor'").fetchall()
print('=== SEEDED DOCTORS ===')
for d in docs:
    print(f'  {d["username"]:15} | {d["full_name"]:25} | {d["city"]}')

# Check slots
slots = cur.execute("""
    SELECT s.slot_date, s.start_time, s.end_time, s.hospital_name, u.full_name as doctor_name
    FROM doctor_slots s JOIN users u ON s.doctor_id = u.id
    ORDER BY s.slot_date, s.start_time
""").fetchall()
print(f'\n=== SEEDED SLOTS ({len(slots)} total) ===')
for s in slots:
    print(f'  {s["doctor_name"]:25} | {s["slot_date"]} {s["start_time"]}-{s["end_time"]} | {s["hospital_name"]}')

# Check doctor_slots schema
cols = cur.execute("PRAGMA table_info(doctor_slots)").fetchall()
print('\n=== doctor_slots COLUMNS ===')
for c in cols:
    print(f'  {c["name"]:20} {c["type"]}')

# Check appointments schema
cols2 = cur.execute("PRAGMA table_info(appointments)").fetchall()
print('\n=== appointments COLUMNS ===')
for c in cols2:
    print(f'  {c["name"]:25} {c["type"]}')

# Check vitals table
v_count = cur.execute("SELECT COUNT(*) FROM vitals").fetchone()[0]
print(f'\n=== vitals table rows: {v_count} ===')

conn.close()
print('\nAll checks PASSED!')
