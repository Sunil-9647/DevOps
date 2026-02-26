FROM python:3.12-slim

# Container-friendly Python behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy both sets of deps
COPY requirements-prod.txt requirements-prod.txt
COPY requirements-dev.txt requirements-dev.txt

# Choose which dependency set to install
ARG TARGET=prod
RUN pip install --no-cache-dir -r requirements-${TARGET}.txt

# Copy only the files we need (keeps image clean)
COPY main.py .

# Create and switch to a non-root user
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/', timeout=2); sys.exit(0)"


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
