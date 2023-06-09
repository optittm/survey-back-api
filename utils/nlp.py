from typing import List, Tuple
from transformers import pipeline, TFRobertaForSequenceClassification, TFCamembertForSequenceClassification, AutoTokenizer

from models.comment import SentimentEnum

class SentimentAnalysis:
    MODELS_FOLDER = "./data/sentiment_models"

    def __init__(self):
        model_en = TFRobertaForSequenceClassification.from_pretrained(self.MODELS_FOLDER + "/english")
        tokenizer_en = AutoTokenizer.from_pretrained(self.MODELS_FOLDER + "/english")
        pipeline_en = pipeline("sentiment-analysis", model=model_en, tokenizer=tokenizer_en)
        
        model_fr = TFCamembertForSequenceClassification.from_pretrained(self.MODELS_FOLDER + "/french")
        tokenizer_fr = AutoTokenizer.from_pretrained(self.MODELS_FOLDER + "/french")
        pipeline_fr = pipeline("sentiment-analysis", model=model_fr, tokenizer=tokenizer_fr)

        self.pipelines = {
            "english": pipeline_en,
            "french": pipeline_fr,
        }

    def analyze(self, text: str, lang: str = "english") -> Tuple[SentimentEnum, float]:
        if lang not in ["english", "french"]:
            raise NotImplementedError()

        result = self.pipelines[lang](text)
        return SentimentEnum(result[0]['label']), result[0]['score']
