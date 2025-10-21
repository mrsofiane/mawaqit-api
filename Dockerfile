FROM python:3.9.6-alpine3.14

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]