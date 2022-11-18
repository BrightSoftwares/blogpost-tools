#FROM python:3-slim
FROM fullbright/post-summarizer:latest

WORKDIR /
ADD src /app
COPY . .

CMD [ "python", "/src/main.py" ]
