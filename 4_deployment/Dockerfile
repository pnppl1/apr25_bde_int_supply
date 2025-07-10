FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8081

CMD ["uvicorn", "sentiment_api:app", "--host", "0.0.0.0", "--port", "8081"]
