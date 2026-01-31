FROM python:3.11-slim

RUN useradd -m runner
WORKDIR /work

RUN pip install --no-cache-dir pytest==8.3.3

USER runner
ENV PYTHONUNBUFFERED=1
