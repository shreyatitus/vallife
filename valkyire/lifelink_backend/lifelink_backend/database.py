import mysql.connector
import os

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("MYSQL_PASSWORD", ""),  # Get from environment or empty
        database="lifelink"
    )

def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("MYSQL_PASSWORD", "")  # Get from environment or empty
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
            age INT,
            weight DECIMAL(5,2),
            height DECIMAL(5,2),
            blood VARCHAR(5),
            password VARCHAR(255),
            donations INT DEFAULT 0,
            points INT DEFAULT 0,
            lastDonation DATE,
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            reportData LONGTEXT,
            reportName VARCHAR(255),
            reportDate DATE,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            response_time INT,
            message TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_decisions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT,
            agent_type VARCHAR(50),
            decision TEXT,
            reasoning TEXT,
            confidence FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donor_patterns (
            id INT AUTO_INCREMENT PRIMARY KEY,
            donor_id INT,
            avg_response_time INT,
            response_rate FLOAT,
            preferred_time VARCHAR(50),
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        ALTER TABLE requests ADD COLUMN IF NOT EXISTS urgency VARCHAR(20) DEFAULT 'medium',
        ADD COLUMN IF NOT EXISTS natural_language_request TEXT,
        ADD COLUMN IF NOT EXISTS agent_analysis TEXT
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
