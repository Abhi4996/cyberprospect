import duckdb

# Make sure you have set your MOTHERDUCK_TOKEN environment variable in PowerShell first!
conn = duckdb.connect('md:cyberprospect')

print('Attaching local database...')
conn.execute("ATTACH 'data/cyberprospect.duckdb' AS local_db")

print('Uploading scans table...')
conn.execute('CREATE OR REPLACE TABLE scans AS SELECT * FROM local_db.scans')

print('Uploading vulns table...')
try:
    conn.execute('CREATE OR REPLACE TABLE vulns AS SELECT * FROM local_db.vulns')
except Exception as e:
    print(f'No vulns found locally to upload: {e}')

print('Uploading org_scores table...')
conn.execute('CREATE OR REPLACE TABLE org_scores AS SELECT * FROM local_db.org_scores')

print('✅ Successfully uploaded all tables to MotherDuck!')
conn.close()
