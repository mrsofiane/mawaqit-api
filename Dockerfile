FROM python:3.14.6-alpine3.24

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]