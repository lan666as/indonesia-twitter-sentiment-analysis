import pandas as pd
import nltk
import re

from sentiment.sentiment import SentimentIntensityAnalyzer
from sentiment.preprocess import preprocess

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split, col, from_json, to_json, schema_of_json, lit, udf, struct, explode
from pyspark.sql.types import StructType, StructField, StringType, DecimalType, ArrayType, LongType, DoubleType

packages = [
    f'org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0',
]

spark = SparkSession \
    .builder \
    .appName("StructuredSentimentAnalysis") \
    .config("spark.jars.packages", ",".join(packages)) \
    .getOrCreate()

schema = StructType([
        StructField("date", StringType(), True),
        StructField("id", LongType(), True),
        StructField("tags", ArrayType(StringType()), True),
        StructField("text", StringType(), True),
    ])

analyzer = SentimentIntensityAnalyzer(lexicon_file="lexicon/combined_indonesia_lexicon.txt", emoji_lexicon="lexicon/translated_emoji_utf8_lexicon.txt")

def calculate_sentiment_score(text):
    return analyzer.polarity_scores(text)["compound"]

kafka_df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("subscribe", "tweets").option("failOnDataLoss", "false").load()
kafka_df_string = kafka_df.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)")

tweets_table = kafka_df_string.select(from_json(col("value"), schema).alias("data")).select("data.*")

preprocess_text = udf(preprocess, StringType())
text_to_sentiment_score = udf(calculate_sentiment_score, DoubleType())

tweets_table = tweets_table.withColumn("clean_text", preprocess_text("text"))
tweets_table = tweets_table.withColumn("sentiment", text_to_sentiment_score("clean_text"))
tweets_table = tweets_table.withColumn("tags", explode("tags"))

tweets_processed_json = tweets_table.select(col("id"), to_json(struct("*"))).toDF("key", "value")

query = tweets_processed_json.selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)").writeStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("topic", "tweets_processed").option("checkpointLocation", "checkpoint").start()

query.awaitTermination()