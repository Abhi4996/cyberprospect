from pyspark.sql.functions import col, when, array_contains, lit, least, greatest, sum as _sum
from etl.config import EXCLUDE_ORGS

def compute_ip_risk_score(df, vulns_df):
    """
    Computes a risk score for each IP/Port scan based on multiple signals.
    """
    print("Computing IP risk scores...")
    
    # 1. Base scan level scoring
    scored = df.withColumn(
        "score_base",
        lit(0) +
        # Outdated software
        when(col("version").isNotNull(), 10).otherwise(0) +
        
        # SSL Issues
        when(col("ssl_expired") == True, 12).otherwise(0) +
        when(array_contains(col("tags"), "self-signed"), 8).otherwise(0) +
        when(array_contains(col("ssl_versions"), "SSLv3") | array_contains(col("ssl_versions"), "TLSv1.0"), 8).otherwise(0) +
        
        # Open Admin / DB Ports
        when(col("port").isin([22, 23, 3389, 8291]), 5).otherwise(0) +
        when(col("port").isin([3306, 5432, 1521, 27017, 6379]), 8).otherwise(0) +
        
        # IoT / Network Devices (detected via info or tags typically, but let's use product for now if it has fortinet/draytek)
        when(col("product").rlike("(?i)fortinet|hikvision|draytek"), 10).otherwise(0) -
        
        # Honeypot penalty
        when(array_contains(col("tags"), "honeypot"), 100).otherwise(0)
    )
    
    # Exclude non-target orgs (CDNs, Cloud Providers)
    scored = scored.withColumn(
        "is_excluded", 
        col("org").isin(EXCLUDE_ORGS) | array_contains(col("tags"), "cdn")
    )
    
    # 2. Vulns level scoring

    
    # A cleaner way in PySpark is computing CVE score first
    v_scored = vulns_df.withColumn(
        "cve_score",
        when(col("cvss") >= 9.0, 25)
        .when(col("cvss") >= 7.0, 15)
        .when(col("cvss") >= 4.0, 8)
        .otherwise(0) +
        when(col("epss") >= 0.5, 10).otherwise(0) + 
        when(col("cve_verified") == True, 5).otherwise(0)
    )
    
    v_agg = v_scored.groupBy("ip_str", "port").agg(
        _sum("cve_score").alias("vuln_score_total")
    )
    
    # 3. Join back
    final_scored = scored.join(v_agg, on=["ip_str", "port"], how="left")
    
    # Fill nulls and cap at 100
    final_scored = final_scored.withColumn("vuln_score_total", when(col("vuln_score_total").isNull(), 0).otherwise(col("vuln_score_total")))
    final_scored = final_scored.withColumn("ip_risk_score", least(lit(100), col("score_base") + col("vuln_score_total")))
    
    # Zero out excluded orgs
    final_scored = final_scored.withColumn("ip_risk_score", when(col("is_excluded") == True, 0).otherwise(col("ip_risk_score")))
    
    return final_scored
