# Base image for a Python environment
FROM python:3.10

# Set working directory inside the container
WORKDIR /app

# Install necessary dependencies
RUN pip install tensorflow requests

# Copy model and entry script into the container
COPY model.py /app/model.py
COPY entry_point.py /app/entry_point.py

# Set the entry point for the container
ENTRYPOINT ["python", "/app/entry_point.py"]