FROM python:3.8.14-alpine3.16

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]