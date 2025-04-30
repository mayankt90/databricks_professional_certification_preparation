from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, BinaryType, StringType, LongType

def process_bronze():
    schema = StructType([
        StructField("key", BinaryType(), True),
        StructField("value", BinaryType(), True),
        StructField("topic", StringType(), True),
        StructField("partition", LongType(), True),
        StructField("offset", LongType(), True),
        StructField("timestamp", LongType(), True)
    ])

    query = (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .schema(schema)
        .load(f"{dataset_bookstore}/kafka-raw")
        .withColumn("timestamp", (F.col("timestamp") / 1000).cast("timestamp"))
        .withColumn("year_month", F.date_format("timestamp", "yyyy-MM"))
        .writeStream
        .option("checkpointLocation", "dbfs:/mnt/demo_pro/checkpoints/bronze")
        .option("mergeSchema", True)
        .partitionBy("topic", "year_month")
        .trigger(availableNow=True)
        .table("bronze")
    )

    query.awaitTermination()
