Survey Back API gives you the possibility to analyze the comments received from your users to automatically identify positive and negative sentiments. This is done thanks to pre-trained Natural Language Processing (NLP) models.

If you have set the variable `USE_SENTIMENT_ANALYSIS` to `True` in the `.env` file of Survey Back API, the models will be downloaded and saved locally (~2GB).
Then they will be pre-loaded into memory to allow for a quicker response when they are needed. **Please allow for around 2GB of additionnal RAM for the models.**

When a comment is posted via the POST /comments route, the language will be automatically detected and call the relevant sentiment analysis model. The language, sentiment (POSITIVE or NEGATIVE) and the confidence score of the model are saved in the database with the comment.

If the `USE_SENTIMENT_ANALYSIS` is set to `False`, the models could not be downloaded, or the comment's language is not supported, then no sentiment analysis will be performed.

Supported language for sentiment analysis:
- English  
Jochen Hartmann, Mark Heitmann, Christian Siebert, Christina Schamp,  
More than a Feeling: Accuracy and Application of Sentiment Analysis,  
International Journal of Research in Marketing, Volume 40, Issue 1, 2023, Pages 75-87, ISSN 0167-8116,  
https://doi.org/10.1016/j.ijresmar.2022.05.005.  
(https://www.sciencedirect.com/science/article/pii/S0167811622000477)  
https://huggingface.co/siebert/sentiment-roberta-large-english

- French  
Théophile Blard,  
French sentiment analysis with BERT, (2020),  
GitHub repository, https://github.com/TheophileBlard/french-sentiment-analysis-with-bert  
https://huggingface.co/tblard/tf-allocine

If you want to do further NLP using the comments from Survey Back API, we have provided a preprocess of the text which includes lowercase, removing punctuation and stopwords, tokenization and lemmatization.  
This returns you a list of word tokens. It is available in the response from the GET /comments endpoint.
