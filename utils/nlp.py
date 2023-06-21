from typing import Optional, Tuple
from langdetect import DetectorFactory, detect, LangDetectException
from transformers import pipeline, TFRobertaForSequenceClassification, TFCamembertForSequenceClassification, AutoTokenizer
import os

from models.comment import SentimentEnum

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

class SentimentAnalysis:
    def __init__(self, config):
        self.analysis_enabled = config.get("use_sentiment_analysis")
        if self.analysis_enabled:
            en_folder = os.path.join(config["sentiment_analysis_models_folder"], "english")
            model_en = TFRobertaForSequenceClassification.from_pretrained(en_folder)
            tokenizer_en = AutoTokenizer.from_pretrained(en_folder)
            pipeline_en = pipeline("sentiment-analysis", model=model_en, tokenizer=tokenizer_en)
            
            fr_folder = os.path.join(config["sentiment_analysis_models_folder"], "french")
            model_fr = TFCamembertForSequenceClassification.from_pretrained(fr_folder)
            tokenizer_fr = AutoTokenizer.from_pretrained(fr_folder)
            pipeline_fr = pipeline("sentiment-analysis", model=model_fr, tokenizer=tokenizer_fr)

            self.pipelines = {
                "en": pipeline_en,
                "fr": pipeline_fr,
            }

    def analyze(self, text: str, lang: str = "en") -> Tuple[Optional[SentimentEnum], Optional[float]]:
        """
        Analyzes the sentiment from the given text.

        Args:
            - text (str): the text to analyze
            - lang (str): the two-character ISO639-1 language code
        
        Returns:
            - The sentiment POSITIVE or NEGATIVE and the confidence score of the model
            - (None, None) if sentiment analysis is disabled
        """
        if self.analysis_enabled:
            if lang not in ["en", "fr"]:
                raise NotImplementedError()

            result = self.pipelines[lang](text)
            return SentimentEnum(result[0]['label']), result[0]['score']
        else:
            return None, None
