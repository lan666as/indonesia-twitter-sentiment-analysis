import pandas as pd
import nltk
import re

from sentiment.sentiment_transformer import SentimentAnalyzerPipeline
from sentiment.geo import PointSpatialJoin
from sentiment.preprocess import preprocess

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col, from_json, to_json, schema_of_json, lit, udf, struct, explode
from pyspark.sql.types import StructType, StructField, StringType, DecimalType, IntegerType, BooleanType, ArrayType, LongType, DoubleType

packages = [
    f'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0',
]

spark = SparkSession \
    .builder \
    .appName("StructuredSentimentAnalysis") \
    .config("spark.jars.packages", ",".join(packages)) \
    .getOrCreate()

schema = StructType([
        StructField("created_at", StringType(), True),
        StructField("id", LongType(), True),
        StructField("author_username", StringType(), True),
        StructField("text", StringType(), True),
        StructField("lat", DoubleType(), True), StructField("long", DoubleType(), True),
        StructField("source", StringType(), True),
        StructField("retweet_count", IntegerType(), True),
        StructField("reply_count", IntegerType(), True),
        StructField("like_count", IntegerType(), True),
        StructField("quote_count", IntegerType(), True),
        StructField("possibly_sensitive", BooleanType(), True),
        StructField("tags", ArrayType(StringType()), True),
    ])

analyzer = SentimentAnalyzerPipeline()
geo = PointSpatialJoin()

def predict_sentiment_label(text):
    return analyzer.predict(text)[0]["label"]

def convert_coordinate_to_province_code(x, y):
    return geo.find_province(x, y)

kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "tweets").option("failOnDataLoss", "false").load()
kafka_df_string = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

tweets_table = kafka_df_string.select(from_json(col("value"), schema).alias("data")).select("data.*")

preprocess_text = udf(preprocess, StringType())
text_to_sentiment_label = udf(predict_sentiment_label, StringType())
point_to_province_iso = udf(convert_coordinate_to_province_code, StringType())

tweets_table = tweets_table.withColumn("clean_text", preprocess_text("text"))
tweets_table = tweets_table.withColumn("sentiment", text_to_sentiment_label("clean_text"))
tweets_table = tweets_table.withColumn("province_code", point_to_province_iso("lat", "long"))

tweets_table = tweets_table.withColumn("tags", explode("tags"))

tweets_processed_json = tweets_table.select(col("id"), to_json(struct("*"))).toDF("key", "value")

query = tweets_processed_json.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)").writeStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("topic", "tweets_processed_v2").option("checkpointLocation", "checkpoint").start()

query.awaitTermination()