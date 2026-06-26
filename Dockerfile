# 1. Use an official, lightweight Python runtime as a parent image
FROM python:3.13-slim

# 2. Set environment variables to optimize Python inside Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container
WORKDIR /code

# 4. Install system dependencies (needed for SQLite and network tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy just the requirements file first to leverage Docker's caching mechanism
COPY requirements.txt /code/

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Copy the rest of your application code into the container
COPY . /code/

# 8. Expose the port FastAPI runs on
EXPOSE 8000

# 9. Run the Uvicorn production server
CMD ["uvicorn", "app.api.server:app", "--host", "0.0.0.0", "--port", "8000"]