FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run the application
# Use shell form to allow variable expansion if needed, but array form is safer for signals
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
