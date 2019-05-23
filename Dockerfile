FROM python:3.7-alpine

WORKDIR /app

RUN apk add build-base

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apk add --no-cache git

COPY . .

COPY files/gitconfig /root/.gitconfig

ENTRYPOINT ["python", "cli.py"]
