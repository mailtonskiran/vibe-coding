import sqlite3

# Path to your SQLite database file
db_path = r'C:\Users\884412\OneDrive - Cognizant\Public\VSCode\workspace\instance\mutual_funds.db'

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# View contents of a specific table (replace 'your_table' with the table name)
try:
    cursor.execute("SELECT * FROM investor;")
    rows = cursor.fetchall()
    print("Number of rows:", len(rows))
    for row in rows:
        print(row)
except Exception as e:
    print("Error:", e)

# Close the connection
conn.close()