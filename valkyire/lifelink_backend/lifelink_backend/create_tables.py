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
        age INT,
        weight FLOAT,
        height FLOAT,
        blood VARCHAR(5),
        password VARCHAR(255),
        latitude FLOAT DEFAULT 0,
        longitude FLOAT DEFAULT 0,
        reportData TEXT,
        reportName VARCHAR(255),
        reportDate DATE,
        status VARCHAR(20) DEFAULT 'pending',
        donations INT DEFAULT 0,
        points INT DEFAULT 0,
        lastDonation VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patientName VARCHAR(255),
        blood VARCHAR(5),
        hospital VARCHAR(255),
        location VARCHAR(255),
        latitude FLOAT DEFAULT 0,
        longitude FLOAT DEFAULT 0,
        status VARCHAR(20) DEFAULT 'pending',
        matched_donor_id INT,
        created_by INT,
        urgency VARCHAR(20),
        natural_language_request TEXT,
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
