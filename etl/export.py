import os
import shutil

def write_parquet(df, output_path, partition_by=None):
    """
    Write DataFrame to Parquet format.
    """
    print(f"Writing to Parquet: {output_path}")
    
    # Clean up existing dir if running locally
    if os.path.exists(output_path):
        print(f"Removing existing directory {output_path}...")
        shutil.rmtree(output_path)
        
    writer = df.write.mode("overwrite")
    if partition_by:
        writer = writer.partitionBy(partition_by)
        
    writer.parquet(output_path)
    print(f"Successfully wrote {output_path}")
