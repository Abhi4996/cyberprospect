from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, DoubleType, 
    LongType, BooleanType, ArrayType, MapType
)

location_schema = StructType([
    StructField("city", StringType()),
    StructField("country_code", StringType()),
    StructField("country_name", StringType()),
    StructField("latitude", DoubleType()),
    StructField("longitude", DoubleType()),
    StructField("region_code", StringType()),
    StructField("area_code", IntegerType())
])

vuln_detail_schema = StructType([
    StructField("cvss", DoubleType()),
    StructField("cvss_version", DoubleType()),
    StructField("cvss_v2", DoubleType()),
    StructField("epss", DoubleType()),
    StructField("ranking_epss", DoubleType()),
    StructField("summary", StringType()),
    StructField("references", ArrayType(StringType())),
    StructField("verified", BooleanType())
])

ssl_cert_schema = StructType([
    StructField("subject", MapType(StringType(), StringType())),
    StructField("issuer", MapType(StringType(), StringType())),
    StructField("expires", StringType()),
    StructField("expired", BooleanType())
])

ssl_schema = StructType([
    StructField("cert", ssl_cert_schema),
    StructField("versions", ArrayType(StringType())),
    StructField("cipher", MapType(StringType(), StringType())),
])

cloud_schema = StructType([
    StructField("provider", StringType()),
    StructField("region", StringType()),
    StructField("service", StringType())
])

http_schema = StructType([
    StructField("status", IntegerType()),
    StructField("title", StringType()),
    StructField("server", StringType()),
    StructField("components", MapType(StringType(), StringType())),
])

shodan_schema = StructType([
    StructField("module", StringType()),
    StructField("crawler", StringType()),
    StructField("id", StringType()),
    StructField("region", StringType())
])

# Top-level banner schema
banner_schema = StructType([
    StructField("ip_str", StringType()),
    StructField("ip", LongType()),
    StructField("port", IntegerType()),
    StructField("transport", StringType()),
    StructField("timestamp", StringType()),
    StructField("hostnames", ArrayType(StringType())),
    StructField("domains", ArrayType(StringType())),
    StructField("org", StringType()),
    StructField("isp", StringType()),
    StructField("asn", StringType()),
    StructField("os", StringType()),
    StructField("product", StringType()),
    StructField("version", StringType()),
    StructField("cpe", ArrayType(StringType())),
    StructField("info", StringType()),
    StructField("tags", ArrayType(StringType())),
    StructField("location", location_schema),
    StructField("cloud", cloud_schema),
    StructField("ssl", ssl_schema),
    StructField("http", http_schema),
    StructField("vulns", MapType(StringType(), vuln_detail_schema)),
    StructField("_shodan", shodan_schema),
    StructField("hash", LongType()),
    StructField("data", StringType()),
])
