import string
from typing import Optional, List
import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

def pos_tagger(nltk_tag: str) -> Optional[str]:
    """
    Converts default NLTK tag (Penn Treebank set) into wordnet tag
    """
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('RB'):
        return wordnet.ADV
    else:         
        return None

def text_preprocess(text: str, lang: str = "english") -> List[str]:
    """
    Does some preprocessing to better analyze a text.
    Lowercase, remove punctuation and stopwords, tokenization and lemmatization

    Returns:
    List of processed tokens
    """
    if lang != "english":
        raise NotImplementedError()
    
    # Lowercase and remove punctuation using translate method
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    
    word_tokens_tagged = nltk.pos_tag(nltk.word_tokenize(text))
    # Convert to wordnet tags
    wordnet_tagged = list(map(lambda x: (x[0], pos_tagger(x[1])), word_tokens_tagged))

    # Remove stop words
    stop_words = set(stopwords.words(lang))
    wordnet_tagged = [w for w in wordnet_tagged if not w[0] in stop_words]
    
    # Lemmatization i.e. converting each word into its base or dictionary form
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(w[0], w[1]) if w[1] is not None else w[0] for w in wordnet_tagged]

    return lemmatized_words
