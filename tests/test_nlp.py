import unittest
import nltk

from utils.nlp import text_preprocess

class TestPreprocess(unittest.TestCase):

    def setUp(self):
        nltk.download("punkt")
        nltk.download("stopwords")
        nltk.download("averaged_perceptron_tagger")
        nltk.download("wordnet")
        self.text = "the cat is sitting with the bats, on the striped mat under many badly flying leaves."

    def test_preprocess(self):
        result = text_preprocess(self.text, "english")
        self.assertEqual(result, ['cat', 'sit', 'bat', 'striped', 'mat', 'many', 'badly', 'fly', 'leaf'])

    def test_unsupported_language(self):
        self.assertRaises(NotImplementedError, text_preprocess, self.text, "arabic")