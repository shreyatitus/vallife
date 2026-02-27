import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="abc123",
        database="lifelink"
    )

def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="abc123"
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS lifelink")
    cursor.close()
    conn.close()
    
    conn = get_db()
    cursor = conn.cursor()
    
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
            lastDonation DATE,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patientName VARCHAR(255),
            blood VARCHAR(5),
            hospital VARCHAR(255),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            status VARCHAR(50) DEFAULT 'pending',
            matched_donor_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            donor_id INT,
            request_id INT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
