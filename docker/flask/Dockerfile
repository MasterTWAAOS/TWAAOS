FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY backend/flask/requirements_flask.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/flask/ .

# Expose port
EXPOSE 5000

# Set environment variables
ENV QUART_APP=app.py
ENV QUART_ENV=production
ENV FASTAPI_BASE_URL=http://fastapi:8000

# Run the application
CMD ["hypercorn", "--bind", "0.0.0.0:5000", "app:app"]
