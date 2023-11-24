FROM node:18

RUN npm install -g markdownlint-cli

COPY . .

RUN ls -laR

CMD ["/bin/bash", "/lint_my_posts.sh"]
