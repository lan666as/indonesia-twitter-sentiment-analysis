from datasets import load_dataset, get_dataset_config_names, concatenate_datasets, load_dataset_builder, Dataset, ClassLabel
import pandas as pd
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer, TextClassificationPipeline

class SentimentAnalyzerPipeline(object):
    """
    Give a sentiment label score to sentences.
    """

    def __init__(self, path='sentiment/model/'):
        self.path = path
        self.config = AutoConfig.from_pretrained(self.path, label2id={"negative":0,"neutral":1,"positive":2}, id2label={0:"negative",1:"neutral",2:"positive"})
        self.model = AutoModelForSequenceClassification.from_pretrained(self.path, config=self.config).to('cpu')
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)
        self.pipeline = TextClassificationPipeline(model=self.model, tokenizer=self.tokenizer, device=-1)

    def predict(self, text):
        return self.pipeline(text)