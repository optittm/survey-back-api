import unittest
import nltk

from utils.nlp import text_preprocess

class TestPreprocess(unittest.TestCase):

    def setUp(self):
        nltk.download("punkt")
        nltk.download("stopwords")
        self.text_en = "the cat is sitting with the bats, on the striped mat under many badly flying leaves."
        self.text_fr = "Elle s'exerce à se Baser sur des 'bilboquets'..."

    def test_preprocess(self):
        result = text_preprocess(self.text_en, "english")
        self.assertEqual(result, ['cat', 'sit', 'bat', 'striped', 'mat', 'many', 'badly', 'fly', 'leave'])
        result = text_preprocess(self.text_fr, "french")
        self.assertEqual(result, ['exercer', 'baser', 'bilboquet'])

    def test_unsupported_language(self):
        self.assertRaises(NotImplementedError, text_preprocess, "", "arabic")