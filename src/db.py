import sqlite3

def main():
    conn = sqlite3.connect('recon_db.db')
    cursor = conn.cursor()

    # Create the 'scans' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id TEXT PRIMARY KEY,
            scan_name TEXT,
            target TEXT
        )
    ''')

    # Create the 'subdomains' table
    cursor.execute('''
        CREATE TABLE subdomains (
            scan_id TEXT,
            subdomain_id INTEGER PRIMARY KEY,
            subdomain_string TEXT,
            open_ports TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
        );
    ''')

    # Create the 'endpoints' table
    cursor.execute('''
        CREATE TABLE endpoints (
            scan_id TEXT,
            subdomain_id INTEGER,
            endpoint_string TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans(scan_id),
            FOREIGN KEY (subdomain_id) REFERENCES subdomains(subdomain_id)
        );
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()

    print("Database and tables created successfully.")

if __name__ == "__main__":
    main()