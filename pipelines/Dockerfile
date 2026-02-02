FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY repository.py .
EXPOSE 4000
CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "4000", "-f", "repository.py"]
