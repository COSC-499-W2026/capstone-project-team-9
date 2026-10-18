FROM python:3.12-slim

WORKDIR /app

# install the project and test dependencies
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir ".[test]"

COPY . .

# launch uvicorn ASGI server in container, run the app on it,
# and bind it to port 8000 so we can access it from outside the container
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]