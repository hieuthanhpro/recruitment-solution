FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY aggregator.py .
COPY benchmark.py .
COPY tests ./tests

RUN mkdir -p results

CMD ["python", "aggregator.py", "--input", "ad_data.csv", "--output", "results"]