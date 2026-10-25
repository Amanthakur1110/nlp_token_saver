FROM python:3.11-slim

WORKDIR /app

# gcc needed for some pip packages; PyMuPDF >= 1.24 ships pre-built wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only torch first to keep image lightweight and isolate download caching
RUN pip install --no-cache-dir torch==2.3.1+cpu --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model at build time so it is ready on first request
RUN python -m spacy download en_core_web_sm

# Download NLTK data at build time
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('punkt_tab')"

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py

# Use flask dev server with reload; swap for gunicorn in production
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]
