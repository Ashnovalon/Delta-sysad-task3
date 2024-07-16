FROM python:3.9-slim

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN pip install --no-cache-dir mysql-connector-python


EXPOSE 12345


CMD ["python", "server.py"]
