FROM python:3.10.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apk update &&\
	apk add --no-cache curl &&\
	apk add --no-cache sqlite

RUN mkdir -p /app/db &&\
	mkdir -p /app/images

COPY db db
COPY main.py .
COPY images images

RUN addgroup -S mercari && adduser -S trainee -G mercari
RUN chown -R trainee:mercari /app/db \
	&& chown -R trainee:mercari /app/images

USER trainee

CMD [ "uvicorn", "main:app" , "--host", "0.0.0.0", "--port", "9000"]
