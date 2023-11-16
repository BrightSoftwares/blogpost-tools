FROM ubuntu

RUN apt update && apt install -y jq

COPY . .

RUN chmod +x /src/check_runner.sh

CMD [ "/bin/bash", "/src/check_runner.sh" ]
