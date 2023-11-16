FROM busybox

RUN apk update && apk upgrade && apk add bash

COPY . .

CMD [ "/bin/bash", "/src/check_runner.sh" ]
