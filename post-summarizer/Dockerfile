FROM python:3-slim

COPY requirements.txt ./

RUN apt-get update && apt-get upgrade && apt-get install -y gcc g++ python3-dev python-dev

#RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel
RUN python -m pip install --upgrade pip
RUN pip install neuralcoref
RUN pip install bert-extractive-summarizer
RUN pip install newspaper3k
RUN pip install python-frontmatter
RUN pip install nltk
RUN pip install markdownify
RUN pip install tomd
RUN pip uninstall spacy
RUN pip install spacy==2.1.0
RUN pip install transformers --upgrade

COPY . .

CMD [ "python", "/src/main.py" ]
