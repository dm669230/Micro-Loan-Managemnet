

FROM python:3.10-slim as builder

WORKDIR /Backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /Backend

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

EXPOSE 8000

CMD ["python", "server.py"]