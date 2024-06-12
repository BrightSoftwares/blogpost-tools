FROM python:3.12

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
#RUN python -m spacy download fr && \
#   python -m spacy download en && \
#   python -m spacy download de && \
#   python -m spacy download es && \
#   python -m spacy download it && \
#   python -m spacy download pt

# RUN npm install -g markdownlint-cli

COPY . .

CMD [ "python", "/src/main.py" ]
