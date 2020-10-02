FROM python:3.7-alpine
LABEL maintainer="AlexFlipnote <root@alexflipnote.dev>"

RUN apk update && apk upgrade

RUN apk add --no-cache git make build-base linux-headers

WORKDIR /discord_bot

COPY index.py ./index.py
COPY config.json ./config.json
COPY requirements.txt ./requirements.txt
COPY ./cogs ./cogs
COPY ./utils ./utils

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "index.py"]
