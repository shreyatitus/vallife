from database import get_db

def add_escalation_table():
    """Add escalation_log table for tracking autonomous escalations"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create escalation_log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS escalation_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            request_id INT NOT NULL,
            action VARCHAR(50) NOT NULL,
            reason TEXT,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (request_id) REFERENCES requests(id)
        )
    """)
    
    # Add escalated_at column to requests if not exists
    try:
        cursor.execute("""
            ALTER TABLE requests 
            ADD COLUMN escalated_at TIMESTAMP NULL
        """)
    except:
        print("escalated_at column already exists")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Escalation table created successfully")

if __name__ == "__main__":
    add_escalation_table()
