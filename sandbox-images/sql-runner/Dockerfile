FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m runner
WORKDIR /work
COPY run_sql_suite.py /work/run_sql_suite.py
USER runner
ENV PYTHONUNBUFFERED=1
