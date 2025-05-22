# Base image for Python
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy your source code into the container
COPY model.py /app/model.py
COPY app.py /app/app.py
COPY templates /app/templates 
COPY model.h5 /app/model.h5


# Install required Python packages
RUN pip install tensorflow flask requests Pillow

# Expose the port used by Flask
EXPOSE 5001

# Run the app
CMD ["python3", "app.py"]