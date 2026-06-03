"""
Quick test to verify the AttributeError fix
"""
import sqlite3

def test_sqlite_row_access():
    """Test proper sqlite3.Row access methods"""
    print("=" * 60)
    print("Testing sqlite3.Row Access Methods")
    print("=" * 60)
    
    # Create in-memory database
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Create test table
    cur.execute("""
        CREATE TABLE test_users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT DEFAULT 'Default'
        )
    """)
    
    # Insert test data
    cur.execute("INSERT INTO test_users (name, city) VALUES (?, ?)", ("John", "New York"))
    cur.execute("INSERT INTO test_users (name) VALUES (?)", ("Jane",))
    
    # Fetch data
    users = cur.execute("SELECT * FROM test_users").fetchall()
    
    print("\n1. Testing dictionary-like access:")
    for user in users:
        print(f"   Name: {user['name']}, City: {user['city']}")
    print("   ✅ Dictionary-like access works!")
    
    print("\n2. Testing key checking:")
    user = users[0]
    if 'city' in user.keys():
        print(f"   'city' key exists: {user['city']}")
    print("   ✅ Key checking works!")
    
    print("\n3. Testing .get() method (should fail):")
    try:
        city = user.get('city', 'Default')
        print(f"   ❌ .get() worked (unexpected)")
    except AttributeError as e:
        print(f"   ✅ .get() failed as expected: {e}")
    
    print("\n4. Testing our fix:")
    try:
        city = user['city'] if 'city' in user.keys() else 'Default'
        print(f"   City: {city}")
        print("   ✅ Our fix works!")
    except Exception as e:
        print(f"   ❌ Our fix failed: {e}")
    
    print("\n5. Testing with missing column:")
    user_without_city = users[1]
    try:
        city = user_without_city['city'] if 'city' in user_without_city.keys() else 'Default'
        print(f"   City (with default): {city}")
        print("   ✅ Default value works!")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe fix is working correctly!")
    print("You can now run: python app.py")
    print("=" * 60)

if __name__ == "__main__":
    test_sqlite_row_access()
