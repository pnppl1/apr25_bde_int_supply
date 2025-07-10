FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

COPY 3_data_consumption/ .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

CMD ["python", "dash_app.py"]
