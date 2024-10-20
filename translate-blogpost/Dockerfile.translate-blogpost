#FROM python:3.6
FROM python:3@sha256:785fef11f44b7393c03d77032fd72e56af8b05442b051a151229145e5fbbcb29

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "/src/main.py" ]
