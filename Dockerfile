FROM python:3.10-slim

# Install MKVToolNix
RUN apt-get update && \
    apt-get install -y \
    wget \
    gnupg \
    && wget -O /etc/apt/keyrings/gpg-pub-moritzbunkus.gpg https://mkvtoolnix.download/gpg-pub-moritzbunkus.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/gpg-pub-moritzbunkus.gpg] https://mkvtoolnix.download/ubuntu/ bionic main" > /etc/apt/sources.list.d/mkvtoolnix.list && \
    apt-get update && \
    apt-get install -y mkvtoolnix && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]