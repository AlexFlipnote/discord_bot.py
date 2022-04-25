FROM python:3.10-alpine
LABEL maintainer="AlexFlipnote <root@alexflipnote.dev>"

LABEL build_date="2022-04-25"
RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers
WORKDIR /discord_bot
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "index.py"]
