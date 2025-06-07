#!/bin/bash

ENV_FILE="$HOME/.sftp_env"

echo "Configuring SSH/SFTP connection details."

read -rp "Remote server IP address or hostname: " REMOTE_HOST
read -rp "SSH/SFTP port (default is 22): " REMOTE_PORT
REMOTE_PORT=${REMOTE_PORT:-22}
read -rp "Remote username: " REMOTE_USER
read -rp "Absolute path to the private SSH key: " SSH_KEY_PATH

if [ ! -f "$SSH_KEY_PATH" ]; then
  echo "Error: The private SSH key does not exist at the specified location."
  exit 1
fi

chmod 600 "$SSH_KEY_PATH"

cat > "$ENV_FILE" <<EOF
export REMOTE_HOST="$REMOTE_HOST"
export REMOTE_PORT="$REMOTE_PORT"
export REMOTE_USER="$REMOTE_USER"
export SSH_KEY_PATH="$SSH_KEY_PATH"
EOF

chmod 600 "$ENV_FILE"

echo "Configuration saved to $ENV_FILE."
echo "Load these variables with: source $ENV_FILE"
