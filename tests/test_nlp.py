import unittest
import nltk

from utils.nlp import NlpPreprocess, SentimentAnalysis

class TestPreprocess(unittest.TestCase):

    def setUp(self):
        nltk.download("punkt")
        nltk.download("stopwords")
        self.nlp_preprocess = NlpPreprocess(config={"use_nlp_preprocess": True})

        self.text_en = "the cat is sitting with the bats, on the striped mat under many badly flying leaves."
        self.text_fr = "Elle s'exerce à se Baser sur des 'bilboquets'..."

    def test_preprocess(self):
        result = self.nlp_preprocess.text_preprocess(self.text_en, "en")
        # lemma of leaves should be leaf in this context but the model isn't 100% accurate
        self.assertEqual(result, ['cat', 'sit', 'bat', 'striped', 'mat', 'many', 'badly', 'fly', 'leave'])
        result = self.nlp_preprocess.text_preprocess(self.text_fr, "fr")
        self.assertEqual(result, ['exercer', 'baser', 'bilboquet'])

    def test_unsupported_language(self):
        self.assertRaises(NotImplementedError, self.nlp_preprocess.text_preprocess, "", "arabic")

    def test_preprocess_disabled(self):
        nlp = NlpPreprocess(config={"use_nlp_preprocess": False})
        result = nlp.text_preprocess("something")
        self.assertIsNone(result)

class TestSentimentAnalysis(unittest.TestCase):

    def test_analysis_disabled(self):
        analysis = SentimentAnalysis(config={"use_sentiment_analysis": False})
        result = analysis.analyze("something")
        self.assertEqual(result, (None, None))
