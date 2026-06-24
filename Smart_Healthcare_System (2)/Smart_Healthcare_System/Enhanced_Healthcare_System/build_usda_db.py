import os
import sys
import csv
import sqlite3

# Set encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("Starting USDA Food Database Builder...")

# Find the dataset path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR))) # Root c:\Project\Smart_Healthcare_System (2)

dataset_dirs = [
    os.path.join(PARENT_DIR, "FoodData_Central_csv_2026-04-30", "FoodData_Central_csv_2026-04-30"),
    os.path.join(PARENT_DIR, "FoodData_Central_csv_2025-12-18", "FoodData_Central_csv_2025-12-18")
]

dataset_path = None
for path in dataset_dirs:
    if os.path.exists(path) and os.path.exists(os.path.join(path, "food.csv")):
        dataset_path = path
        break

if not dataset_path:
    print(f"Error: USDA Dataset not found in paths: {dataset_dirs}")
    sys.exit(1)

print(f"Using USDA dataset at: {dataset_path}")

target_fdc_ids = set()

# 1. Load FDC IDs from survey_fndds_food.csv (Generic meals/dishes)
fndds_path = os.path.join(dataset_path, "survey_fndds_food.csv")
if os.path.exists(fndds_path):
    print("Reading survey_fndds_food.csv...")
    with open(fndds_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_fdc_ids.add(row['fdc_id'])
    print(f"Loaded {len(target_fdc_ids)} FNDDS food IDs.")

# 2. Load FDC IDs from sr_legacy_food.csv (Generic raw/whole foods)
sr_path = os.path.join(dataset_path, "sr_legacy_food.csv")
if os.path.exists(sr_path):
    print("Reading sr_legacy_food.csv...")
    with open(sr_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_fdc_ids.add(row['fdc_id'])
    print(f"Updated with SR Legacy. Total IDs: {len(target_fdc_ids)}")

# 3. Load FDC IDs from foundation_food.csv
foundation_path = os.path.join(dataset_path, "foundation_food.csv")
if os.path.exists(foundation_path):
    print("Reading foundation_food.csv...")
    with open(foundation_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            target_fdc_ids.add(row['fdc_id'])
    print(f"Updated with Foundation Food. Total IDs: {len(target_fdc_ids)}")

# 4. Read food.csv to map descriptions
food_details = {}
food_path = os.path.join(dataset_path, "food.csv")
print("Reading food.csv to map descriptions...")
with open(food_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        fdc_id = row['fdc_id']
        if fdc_id in target_fdc_ids:
            food_details[fdc_id] = {
                'fdc_id': int(fdc_id),
                'name': row['description'].strip(),
                'calories': 0.0,
                'protein': 0.0,
                'carbs': 0.0,
                'fat': 0.0
            }

print(f"Mapped descriptions for {len(food_details)} foods.")

# 5. Read food_nutrient.csv to map nutrition (Calories, Protein, Carbs, Fat)
# Nutrient IDs:
# 1008: Energy (KCAL)
# 1003: Protein (G)
# 1005: Carbohydrate, by difference (G)
# 1004: Total lipid (fat) (G)
nutrient_path = os.path.join(dataset_path, "food_nutrient.csv")
print("Reading food_nutrient.csv (this might take a few seconds)...")

count = 0
with open(nutrient_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Get header to verify indices
    header = next(reader)
    # Header: "id","fdc_id","nutrient_id","amount",...
    fdc_idx = header.index("fdc_id")
    nut_idx = header.index("nutrient_id")
    amt_idx = header.index("amount")
    
    for row in reader:
        if not row or len(row) <= max(fdc_idx, nut_idx, amt_idx):
            continue
        fdc_id = row[fdc_idx]
        if fdc_id in food_details:
            nut_id = row[nut_idx]
            try:
                amt = float(row[amt_idx])
            except ValueError:
                amt = 0.0
            
            if nut_id == '1008': # Calories
                food_details[fdc_id]['calories'] = amt
            elif nut_id == '1003': # Protein
                food_details[fdc_id]['protein'] = amt
            elif nut_id == '1005': # Carbs
                food_details[fdc_id]['carbs'] = amt
            elif nut_id == '1004': # Fat
                food_details[fdc_id]['fat'] = amt
            
            count += 1
            if count % 100000 == 0:
                print(f"Processed {count} nutrient records...")

print("Finished reading nutrients. Saving to SQLite database...")

# 6. Save to SQLite database
db_path = os.path.join(BASE_DIR, "healthcare.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Drop existing table if exists to start fresh
cur.execute("DROP TABLE IF EXISTS usda_food_nutrition")
cur.execute("""
CREATE TABLE usda_food_nutrition (
    fdc_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0
)
""")

# Prepare values for bulk insert
insert_data = [
    (item['fdc_id'], item['name'], item['calories'], item['protein'], item['carbs'], item['fat'])
    for item in food_details.values()
]

# Bulk insert
cur.executemany("""
INSERT INTO usda_food_nutrition (fdc_id, name, calories, protein, carbs, fat)
VALUES (?, ?, ?, ?, ?, ?)
""", insert_data)

# Create index on name for fast lookups
cur.execute("CREATE INDEX IF NOT EXISTS idx_usda_food_name ON usda_food_nutrition(name)")

# Create FTS5 virtual table if FTS5 is supported (otherwise fall back silently)
try:
    cur.execute("DROP TABLE IF EXISTS usda_food_nutrition_fts")
    cur.execute("""
    CREATE VIRTUAL TABLE usda_food_nutrition_fts USING fts5(
        fdc_id,
        name,
        calories,
        protein,
        carbs,
        fat,
        content='usda_food_nutrition',
        content_rowid='fdc_id'
    )
    """)
    # Populate FTS
    cur.execute("""
    INSERT INTO usda_food_nutrition_fts(rowid, fdc_id, name, calories, protein, carbs, fat)
    SELECT fdc_id, fdc_id, name, calories, protein, carbs, fat FROM usda_food_nutrition
    """)
    print("FTS5 search index built successfully!")
except sqlite3.OperationalError as e:
    print(f"FTS5 not supported: {e}. Falling back to standard indexes.")

conn.commit()

# Verify row counts
cur.execute("SELECT COUNT(*) FROM usda_food_nutrition")
total_rows = cur.fetchone()[0]
print(f"Successfully loaded {total_rows} USDA foods with exact nutrients into usda_food_nutrition table in healthcare.db!")

conn.close()
print("USDA database build complete!")
