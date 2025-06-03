#!/bin/bash

echo "*/10 * * * * /app/transfer_zips.sh >> /app/static/zip_cron.log 2>&1" | crontab -
touch /app/static/zip_cron.log
touch /app/static/last_upload.txt

cron
exec python app.py
