from typing import List
import spacy
import nltk
from nltk.corpus import stopwords


def text_preprocess(text: str, lang: str = "english") -> List[str]:
    """
    Does some preprocessing to better analyze a text.
    Lowercase, remove punctuation and stopwords, tokenization and lemmatization

    Returns:
    List of processed tokens
    """
    if lang == "english":
        nlp = spacy.load("en_core_web_md")
    elif lang == "french":
        nlp = spacy.load("fr_core_news_md")
    else:
        raise NotImplementedError()
    
    word_tokens = nltk.word_tokenize(text)
    
    doc = nlp(text)
    pos_lemmas = [[token.pos_, token.lemma_] for token in doc]
    
    # Remove stop words and punctuation
    stop_words = set(stopwords.words(lang))
    word_tokens = [w[1] for w in pos_lemmas if w[1] not in stop_words and w[0] != 'PUNCT']
    
    return word_tokens
