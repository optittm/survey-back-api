from typing import List, Tuple
import os
# Sets Tensorflow's logs to ERROR
# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 
from transformers import pipeline, TFRobertaForSequenceClassification, TFCamembertForSequenceClassification, AutoTokenizer

from models.comment import SentimentEnum


# import spacy
# from nltk.corpus import stopwords
# def text_preprocess(text: str, lang: str = "english") -> List[str]:
#     """
#     Does some preprocessing to better analyze a text.
#     Lowercase, remove punctuation and stopwords, tokenization and lemmatization

#     Returns:
#     List of processed tokens
#     """
#     if lang == "english":
#         nlp = spacy.load("en_core_web_md")
#     elif lang == "french":
#         nlp = spacy.load("fr_core_news_md")
#     else:
#         raise NotImplementedError()
    
#     doc = nlp(text)
#     pos_lemmas = [[token.pos_, token.lemma_] for token in doc]
    
#     # Remove stop words and punctuation
#     stop_words = set(stopwords.words(lang))
#     word_tokens = [w[1] for w in pos_lemmas if w[1] not in stop_words and w[0] != 'PUNCT']
    
#     return word_tokens

def sentiment_analysis(text: str, lang: str = "english") -> Tuple[SentimentEnum, float]:
    if lang == "english":
        model = TFRobertaForSequenceClassification.from_pretrained("./data/sentiment_models/english")
        tokenizer = AutoTokenizer.from_pretrained("./data/sentiment_models/english")
    elif lang == "french":
        model = TFCamembertForSequenceClassification.from_pretrained("./data/sentiment_models/french")
        tokenizer = AutoTokenizer.from_pretrained("./data/sentiment_models/french")
    else:
        raise NotImplementedError()

    sentiment_analysis = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    result = sentiment_analysis(text)
    return SentimentEnum(result[0]['label']), result[0]['score']

if __name__ == "__main__":
    str_en = "I've seen better"
    str_fr = "C'est pas mal, mais assez utile"

    sentiment_analysis(str_en, "english")
    sentiment_analysis(str_fr, "french")