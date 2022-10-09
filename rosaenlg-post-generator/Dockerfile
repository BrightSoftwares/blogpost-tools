FROM node:latest

WORKDIR /app

#COPY requirements.txt ./

RUN npm install -g rosaenlg-packager rosaenlg-node-server rosaenlg-cli \
		@wcj/html-to-markdown-cli

#RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "/app/src/generate_posts.sh" ]
