import duckdb
import os

# Adjust path depending on where Streamlit is run from
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "cyberprospect.duckdb")
PARQUET_SCANS = os.path.join(BASE_DIR, "data", "parquet", "scans", "**", "*.parquet")
PARQUET_VULNS = os.path.join(BASE_DIR, "data", "parquet", "vulns", "*.parquet")

def get_connection():
    """Returns a DuckDB connection, using MotherDuck if a token is configured."""
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        try:
            import streamlit as st
            if "MOTHERDUCK_TOKEN" in st.secrets:
                token = st.secrets["MOTHERDUCK_TOKEN"]
        except:
            pass

    if token:
        os.environ["MOTHERDUCK_TOKEN"] = token
        conn = duckdb.connect("md:cyberprospect")
    else:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = duckdb.connect(DB_PATH, read_only=False)

    # Ensure the AI cache table exists whenever we request a connection.
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_pitches (
                org VARCHAR PRIMARY KEY,
                pitch_text TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tone VARCHAR,
                focus_area VARCHAR
            )
        """)
    except Exception as e:
        # Ignore errors if the database is read-only or temporarily locked
        pass

    return conn

def init_db(force=False):
    """Initialize views and tables in DuckDB, caching org_scores as a table."""
    conn = get_connection()
    try:
        # Create views over Parquet (ignoring missing files for now if they don't exist yet)
        if os.path.exists(os.path.join(BASE_DIR, "data", "parquet")):
            # Safe drop of scans (handles both table and view forms)
            for drop_type in ["VIEW", "TABLE"]:
                try:
                    conn.execute(f"DROP {drop_type} IF EXISTS scans")
                except:
                    pass
            
            conn.execute(f"CREATE OR REPLACE VIEW scans AS SELECT * FROM read_parquet('{PARQUET_SCANS}', union_by_name=true)")
            
            # Safe drop of vulns (handles both table and view forms)
            for drop_type in ["VIEW", "TABLE"]:
                try:
                    conn.execute(f"DROP {drop_type} IF EXISTS vulns")
                except:
                    pass
                    
            # Vulns might not exist if sample has no vulns
            try:
                conn.execute(f"CREATE OR REPLACE VIEW vulns AS SELECT * FROM read_parquet('{PARQUET_VULNS}', union_by_name=true)")
            except:
                pass
                
            # Determine if we need to rebuild the materialized table
            rebuild = force
            from datetime import datetime
            
            # Check if table exists
            tables = [r[0] for r in conn.execute("SHOW TABLES").fetchall()]
            if 'org_scores' not in tables:
                rebuild = True
            elif not rebuild:
                try:
                    # Check if it has been more than 10 minutes (600 seconds) since last refresh
                    conn.execute("CREATE TABLE IF NOT EXISTS db_metadata (key VARCHAR PRIMARY KEY, value VARCHAR)")
                    last_refresh = conn.execute("SELECT value FROM db_metadata WHERE key = 'last_refresh_time'").fetchone()
                    if last_refresh:
                        last_time = datetime.fromisoformat(last_refresh[0])
                        if (datetime.now() - last_time).total_seconds() > 600:
                            rebuild = True
                    else:
                        rebuild = True
                except Exception as e:
                    rebuild = True
            
            if rebuild:
                # Re-create materialized table of org scores for fast dashboarding
                conn.execute("DROP TABLE IF EXISTS org_scores")
                conn.execute("""
                    CREATE TABLE org_scores AS
                    WITH base AS (
                        SELECT 
                            org,
                            COUNT(DISTINCT ip_str) as total_ips,
                            COUNT(DISTINCT ip_str || ':' || CAST(port AS VARCHAR)) as total_open_ports,
                            MAX(ip_risk_score) as max_risk_score,
                            AVG(ip_risk_score) as avg_risk_score,
                            LIST(DISTINCT country_name) as countries
                        FROM scans 
                        WHERE org IS NOT NULL AND is_excluded = FALSE
                        GROUP BY org
                    )
                    SELECT 
                        *,
                        LEAST(100.0, (max_risk_score * 0.7) + (avg_risk_score * 0.3) + LEAST(10.0, total_ips * 0.5)) as combined_risk_score
                    FROM base
                """)
                
                # Update last refresh time
                conn.execute("CREATE TABLE IF NOT EXISTS db_metadata (key VARCHAR PRIMARY KEY, value VARCHAR)")
                conn.execute("INSERT OR REPLACE INTO db_metadata (key, value) VALUES ('last_refresh_time', ?)", [datetime.now().isoformat()])
        
        # Create AI cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_pitches (
                org VARCHAR PRIMARY KEY,
                pitch_text TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tone VARCHAR,
                focus_area VARCHAR
            )
        """)
    except Exception as e:
        import streamlit as st
        st.error(f"Error initializing DB: {e}")
        raise e
    finally:
        conn.close()

def test_connection():
    try:
        conn = get_connection()
        res = conn.execute("SELECT 1").fetchone()
        conn.close()
        return res[0] == 1
    except:
        return False
