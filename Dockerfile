FROM python:3.7
MAINTAINER AlexFlipnote <root@alexflipnote.dev>

WORKDIR /discord_bot
COPY . /discord_bot

RUN pip install --no-cache-dir -r requirements.txt

CMD python index.py
