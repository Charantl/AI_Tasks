FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY run_gateway.py ./

COPY ./app ./app

COPY alembic.ini ./

COPY entrypoint.sh ./
ENTRYPOINT ["/app/entrypoint.sh"] 