FROM python:3.10-slim
RUN echo 'Acquire::http::Timeout "120";' > /etc/apt/apt.conf.d/99timeout && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libc-dev && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt
COPY graph_ssl_threat.py graph_runner.py ./
ENV MPLBACKEND=Agg
CMD ["python", "graph_runner.py"]