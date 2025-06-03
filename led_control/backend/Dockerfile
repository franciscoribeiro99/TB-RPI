FROM python:3.9-slim

WORKDIR /app

# install packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    libtiff-dev \
    libturbojpeg0 \
    cron \
    openssh-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# copy files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy scripts
COPY transfer_zips.sh start.sh ./
RUN chmod +x /app/transfer_zips.sh /app/start.sh

# Copy
COPY . .

# expose port
EXPOSE 5000

# run script
CMD ["/bin/bash", "./start.sh"]
