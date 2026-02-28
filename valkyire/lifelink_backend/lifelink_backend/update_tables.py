import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123",
    database="lifelink"
)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0")
except:
    print("latitude column already exists")

try:
    cursor.execute("ALTER TABLE users ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0")
except:
    print("longitude column already exists")

try:
    cursor.execute("ALTER TABLE users MODIFY lastDonation DATE")
except:
    print("lastDonation already DATE type")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0")
except:
    print("requests latitude already exists")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0")
except:
    print("requests longitude already exists")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN status VARCHAR(50) DEFAULT 'pending'")
    print("✅ status column added")
except:
    print("status column already exists")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN created_by INT")
    print("✅ created_by column added")
except:
    print("created_by column already exists")

try:
    cursor.execute("ALTER TABLE requests ADD COLUMN matched_donor_id INT")
    print("✅ matched_donor_id column added")
except:
    print("matched_donor_id column already exists")

conn.commit()
print("✅ All columns updated!")
cursor.close()
conn.close()
