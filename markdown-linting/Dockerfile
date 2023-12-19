FROM node:18

RUN npm install -g markdownlint-cli markdownlint-rule-search-replace markdownlint-rule-helpers

RUN mkdir /app/
WORKDIR /app/

COPY . .

RUN ls -lRa /app/

CMD ["/bin/bash", "/app/lint_my_posts.sh"]
