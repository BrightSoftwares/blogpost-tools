FROM node:current-stretch-slim

npm i -g netlify-cli

ADD entrypoint.sh /entrypoint.sh
ADD action.yml /action.yml

ENTRYPOINT ["/entrypoint.sh"]
