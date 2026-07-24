# Dockerfile
FROM python:3.12-slim

# Installer les dépendances système pour PostgreSQL et les outils de construction généraux
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables using modern key=value format
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# compile le CSS Tailwind
RUN python manage.py tailwind build
RUN python manage.py collectstatic --noinput --clear

CMD python manage.py migrate && \
    gunicorn config.wsgi --bind 0.0.0.0:$PORT

# Expose the port
EXPOSE 8080
