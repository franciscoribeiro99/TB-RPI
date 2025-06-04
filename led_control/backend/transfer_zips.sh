#!/bin/bash

src_dir="/app/static/images"
ssh_key="${SSH_KEY_PATH}"
remote_user="${REMOTE_USER}"
remote_host="${REMOTE_HOST}"
remote_port="${REMOTE_PORT:-22}"
remote_base_dir="Tb"
logfile="/app/static/zip_cron.log"
threshold=40  # Disk usage threshold in percent
lockfile="/tmp/transfer_zips.lock"
tmp_list="/tmp/jpg_list_$$.txt"

touch "$logfile"

# Prevent overlapping runs
if [ -f "$lockfile" ]; then
    echo "$(date): transfer already running, exiting." >> "$logfile"
    exit 0
fi
touch "$lockfile"

# Check disk usage
used=$(df "$src_dir" | awk 'NR==2 {gsub("%", "", $5); print $5}')
if [[ "$1" != "--force" && "$used" -lt "$threshold" ]]; then
    echo "$(date): disk ok ($used%), no transfer" >> "$logfile"
    rm -f "$lockfile"
    exit 0
fi

echo "$(date): starting transfer (disk $used%)" >> "$logfile"

# List all JPG files except latest.jpg
find "$src_dir" -type f -name '*.jpg' ! -name 'latest.jpg' > "$tmp_list"
jpg_count=$(wc -l < "$tmp_list")

if [ "$jpg_count" -eq 0 ]; then
    echo "$(date): no jpg files to archive" >> "$logfile"
    rm -f "$lockfile" "$tmp_list"
    exit 0
fi

timestamp=$(date +"%Y%m%d_%H%M%S")
day_dir=$(date +"%Y-%m-%d")
tar_file="/app/static/capture_${timestamp}.tar"

# Create TAR
tar -cf "$tar_file" -T "$tmp_list" --transform 's|^/||' 2>> "$logfile"
if [ $? -ne 0 ]; then
    echo "$(date): error during tar creation" >> "$logfile"
    rm -f "$lockfile" "$tmp_list"
    exit 1
fi

echo "$(date): created $tar_file with $jpg_count jpg files" >> "$logfile"

# Upload via SFTP to dated folder
sftp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$ssh_key" -P "$remote_port" "$remote_user@$remote_host" <<EOF
mkdir $remote_base_dir/$day_dir
cd $remote_base_dir/$day_dir
put "$tar_file"
EOF

if [ $? -eq 0 ]; then
    echo "$(date): sent $tar_file and deleting archived files" >> "$logfile"
    xargs -r rm -f < "$tmp_list"
    rm -f "$tar_file"
    date "+%Y-%m-%d %H:%M:%S" > /app/static/last_upload.txt
else
    echo "$(date): failed to send $tar_file" >> "$logfile"
fi

rm -f "$lockfile" "$tmp_list"
