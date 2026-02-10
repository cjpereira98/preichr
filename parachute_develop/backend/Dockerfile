# Build Stage
FROM python:3.12.6-slim
WORKDIR /parachute/backend
COPY . .
RUN chmod +x run_main.sh
RUN apt-get update && \
    apt-get install -y libkrb5-dev build-essential curl
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt


# Production Stage
EXPOSE 8000
CMD ["./run_main.sh"]
