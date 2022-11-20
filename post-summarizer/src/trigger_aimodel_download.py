from summarizer import Summarizer
import nltk
import os

os.environ['TRANSFORMERS_CACHE'] = '/root/.cache/huggingface/transformers/'

nltk.download('punkt')
model = Summarizer()
