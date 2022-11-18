from summarizer import Summarizer
import nltk
import os

os.environ['TRANSFORMERS_CACHE'] = '/transformers/cache'

nltk.download('punkt')
model = Summarizer()
