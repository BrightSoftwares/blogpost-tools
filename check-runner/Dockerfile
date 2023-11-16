FROM ubuntu

RUN apt update && apt install -y jq curl

COPY . .

RUN chmod u+x /src/check_runner.sh

CMD [ "/src/check_runner.sh" ]
