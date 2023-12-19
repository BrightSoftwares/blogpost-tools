FROM node:18

RUN npm install -g markdownlint-cli markdownlint-rule-search-replace markdownlint-rule-helpers

COPY . .

CMD ["/bin/bash", "/lint_my_posts.sh"]
