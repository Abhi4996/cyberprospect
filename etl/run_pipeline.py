import os
from etl.config import INPUT_FILE, PARQUET_DIR
from etl.ingest import init_spark, ingest_data
from etl.transform import clean_and_flatten, deduplicate_scans, extract_vulnerabilities
from etl.score import compute_ip_risk_score
from etl.export import write_parquet

def run():
    print("Starting ETL Pipeline...")
    
    # Set HADOOP_HOME for Windows compatibility with PySpark
    if os.name == 'nt':
        os.environ['HADOOP_HOME'] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hadoop")
        os.environ['PATH'] = os.path.join(os.environ['HADOOP_HOME'], "bin") + os.pathsep + os.environ['PATH']
        
    spark = init_spark()
    
    # 1. Ingest
    raw_df = ingest_data(spark, INPUT_FILE)
    
    # 2. Transform
    flat_df = clean_and_flatten(raw_df)
    dedup_df = deduplicate_scans(flat_df)
    
    # 3. Vulns
    vulns_df = extract_vulnerabilities(dedup_df)
    
    # 4. Score
    scored_df = compute_ip_risk_score(dedup_df, vulns_df)
    
    # 5. Export
    scans_out = os.path.join(PARQUET_DIR, "scans")
    vulns_out = os.path.join(PARQUET_DIR, "vulns")
    
    # Cache before writing since it's used multiple times or heavily computed
    scored_df.cache()
    
    # We partition by country_code, handle nulls gracefully
    # Replace null country_code with 'unknown' for partitioning
    from pyspark.sql.functions import col, when
    export_scans = scored_df.withColumn("country_code", when(col("country_code").isNull(), "unknown").otherwise(col("country_code")))
    
    write_parquet(export_scans, scans_out, partition_by="country_code")
    write_parquet(vulns_df, vulns_out)
    
    scored_df.unpersist()
    print("ETL Pipeline finished successfully!")

if __name__ == "__main__":
    run()
