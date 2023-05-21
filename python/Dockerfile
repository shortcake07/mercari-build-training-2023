FROM python:3.10.11-alpine

WORKDIR /app

COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk update &&\
	apk add --no-cache curl &&\
	apk add --no-cache sqlite

RUN mkdir -p /app/db &&\
	mkdir -p /app/python

COPY db db
COPY python python

RUN addgroup -S mercari && adduser -S trainee -G mercari
RUN chown -R trainee:mercari /app/db &&\
	chown -R trainee:mercari /app/images &&\
	chmod 777 /app/items.json

USER trainee

CMD [ "uvicorn", "main:app" , "--host", "0.0.0.0", "--port", "9000"]
