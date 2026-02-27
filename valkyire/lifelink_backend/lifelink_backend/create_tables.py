import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123"
)
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS lifelink")
cursor.execute("USE lifelink")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255) UNIQUE,
        phone VARCHAR(20),
        blood VARCHAR(5),
        password VARCHAR(255),
        donations INT DEFAULT 0,
        points INT DEFAULT 0,
        lastDonation VARCHAR(50)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patientName VARCHAR(255),
        blood VARCHAR(5),
        hospital VARCHAR(255),
        location VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
print("Tables created successfully!")

cursor.execute("SHOW TABLES")
for table in cursor:
    print(f"Table: {table[0]}")

cursor.close()
conn.close()
