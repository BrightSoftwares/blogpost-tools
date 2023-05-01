FROM fullbright/openai-generate-blogpost:latest

WORKDIR /
ADD src /app
COPY . .

CMD [ "python", "/src/main.py" ]
