from pyspark.sql.functions import col, explode, when, to_timestamp, row_number
from pyspark.sql.window import Window

def clean_and_flatten(df):
    """
    Flatten nested structures, parse timestamps, and extract essential fields
    to top-level columns.
    """
    print("Flattening and cleaning data...")
    # Extract needed fields from structs
    res = df.select(
        "ip_str",
        "port",
        "transport",
        "timestamp",
        "org",
        "isp",
        "asn",
        "product",
        "version",
        "info",
        "tags",
        
        # Location fields
        col("location.city").alias("city"),
        col("location.country_name").alias("country_name"),
        col("location.country_code").alias("country_code"),
        col("location.latitude").alias("latitude"),
        col("location.longitude").alias("longitude"),
        
        # SSL fields
        col("ssl.cert.expired").alias("ssl_expired"),
        col("ssl.versions").alias("ssl_versions"),
        
        # HTTP fields
        col("http.server").alias("http_server"),
        col("http.title").alias("http_title"),
        
        # Cloud fields
        col("cloud.provider").alias("cloud_provider"),
        col("cloud.service").alias("cloud_service"),
        
        # Vulns
        "vulns"
    )
    
    # Parse timestamp
    res = res.withColumn("timestamp", to_timestamp("timestamp"))
    return res

def deduplicate_scans(df):
    """
    Keep only the latest scan for each (ip_str, port) combination
    """
    print("Deduplicating scans...")
    windowSpec = Window.partitionBy("ip_str", "port").orderBy(col("timestamp").desc())
    deduped = df.withColumn("row_num", row_number().over(windowSpec)) \
                .filter(col("row_num") == 1) \
                .drop("row_num")
    return deduped

def extract_vulnerabilities(df):
    """
    Explode the vulns dict into a separate dataframe of (ip_str, port, cve_id, details)
    """
    print("Extracting vulnerabilities...")
    vulns_df = df.filter(col("vulns").isNotNull()) \
        .select("ip_str", "port", "org", explode("vulns").alias("cve_id", "cve_detail")) \
        .select(
            "ip_str", 
            "port", 
            "org",
            "cve_id",
            col("cve_detail.cvss").alias("cvss"),
            col("cve_detail.epss").alias("epss"),
            col("cve_detail.summary").alias("cve_summary"),
            col("cve_detail.verified").alias("cve_verified")
        )
    return vulns_df
