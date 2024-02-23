FROM python:3.8.14-alpine3.16

ENV REDIS_HOST localhost
ENV REDIS_PORT 6379
ENV USE_REDIS false

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]