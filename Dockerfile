FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/platform

WORKDIR /app
COPY platform/requirements.txt /app/platform/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/platform/requirements.txt

COPY platform /app/platform
COPY schemas /app/schemas
COPY tools /app/tools

EXPOSE 8080
CMD ["python", "platform/run.py"]
