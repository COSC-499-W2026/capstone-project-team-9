# Build order: layers go from least to most frequently changed, so a code
# change only rebuilds the last step or two and everything heavy stays cached.
#   1. torch (rarely changes)
#   2. third-party dependencies (change when pyproject.toml changes)
#   3. EasyOCR model weights (change when dependencies change)
#   4. project files (change on almost every commit)

FROM python:3.12-slim

WORKDIR /app

# Install CPU-only torch first so easyocr doesn't pull the huge CUDA build
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install third-party dependencies only, reading them straight from pyproject.toml with uv
COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/uv \
    pip install uv && \
    uv pip install --system -r pyproject.toml --extra test

# Bake EasyOCR model weights into the image so nothing downloads at runtime
RUN python -c "import easyocr; easyocr.Reader(['en'], gpu=False)"

# Copy project files last, since they change most often
COPY scripts/ ./scripts/
COPY src/ ./src/

# Expose port 8000 and launch the app with uvicorn
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]