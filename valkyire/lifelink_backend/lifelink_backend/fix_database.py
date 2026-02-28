import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="abc123",
    database="lifelink"
)
cursor = conn.cursor()

def add_column_if_not_exists(table, column, definition):
    try:
        cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
        print(f"Column {table}.{column} already exists")
    except:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        conn.commit()
        print(f"Added {table}.{column}")

# Add missing columns to users table
add_column_if_not_exists("users", "age", "INT")
add_column_if_not_exists("users", "weight", "FLOAT")
add_column_if_not_exists("users", "height", "FLOAT")
add_column_if_not_exists("users", "latitude", "FLOAT DEFAULT 0")
add_column_if_not_exists("users", "longitude", "FLOAT DEFAULT 0")
add_column_if_not_exists("users", "reportData", "TEXT")
add_column_if_not_exists("users", "reportName", "VARCHAR(255)")
add_column_if_not_exists("users", "reportDate", "DATE")
add_column_if_not_exists("users", "status", "VARCHAR(20) DEFAULT 'pending'")
add_column_if_not_exists("users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

# Add missing columns to requests table
add_column_if_not_exists("requests", "latitude", "FLOAT DEFAULT 0")
add_column_if_not_exists("requests", "longitude", "FLOAT DEFAULT 0")
add_column_if_not_exists("requests", "status", "VARCHAR(20) DEFAULT 'pending'")
add_column_if_not_exists("requests", "matched_donor_id", "INT")
add_column_if_not_exists("requests", "created_by", "INT")
add_column_if_not_exists("requests", "urgency", "VARCHAR(20)")
add_column_if_not_exists("requests", "natural_language_request", "TEXT")

cursor.close()
conn.close()
print("\nDatabase updated successfully!")
