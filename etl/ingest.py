from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from etl.schema import banner_schema
import os

def init_spark() -> SparkSession:
    """Initialize PySpark session tailored for local processing."""
    return SparkSession.builder \
        .master("local[*]") \
        .appName("CyberProspect-ETL") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "100") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.jsonGenerator.ignoreNullFields", "true") \
        .config("spark.sql.parquet.compression.codec", "snappy") \
        .getOrCreate()

def ingest_data(spark: SparkSession, input_path: str):
    """
    Read Shodan JSONL data using explicit schema.
    PySpark natively handles .zst compression if the Hadoop binary supports it,
    otherwise we might need to uncompress it first or use .gz.
    For this sample, we use the .json directly.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
        
    print(f"Reading data from {input_path}...")
    df = spark.read.schema(banner_schema).json(input_path)
    return df

if __name__ == "__main__":
    from etl.config import INPUT_FILE
    spark = init_spark()
    df = ingest_data(spark, INPUT_FILE)
    df.printSchema()
    print(f"Total rows read: {df.count()}")
