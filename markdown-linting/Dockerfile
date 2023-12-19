FROM node:18

RUN mkdir /app/
WORKDIR /app/

RUN npm install -g markdownlint-cli 
RUN npm install markdownlint-rule-search-replace
RUN npm install markdownlint-rule-helpers


COPY . .

RUN ls -lRa /app/

CMD ["/bin/bash", "/app/lint_my_posts.sh"]
