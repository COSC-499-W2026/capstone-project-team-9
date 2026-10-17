FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

EXPOSE 8000

# Default command that runs when container starts
# launches uvicorn ASGI server, runs the app on it, and binds it to port 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]