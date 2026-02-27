import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123",
    database="lifelink"
)
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0")
cursor.execute("ALTER TABLE users ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0")
cursor.execute("ALTER TABLE users MODIFY lastDonation DATE")

cursor.execute("ALTER TABLE requests ADD COLUMN latitude DECIMAL(10, 8) DEFAULT 0")
cursor.execute("ALTER TABLE requests ADD COLUMN longitude DECIMAL(11, 8) DEFAULT 0")

conn.commit()
print("Columns added successfully!")
cursor.close()
conn.close()
