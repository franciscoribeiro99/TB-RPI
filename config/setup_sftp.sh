#!/bin/bash

ENV_FILE="$HOME/.sftp_env"

echo "Configuration des informations de connexion SSH/SFTP."

read -rp "Adresse IP ou nom d'hôte du serveur distant : " REMOTE_HOST
read -rp "Port SSH/SFTP (par défaut 22) : " REMOTE_PORT
REMOTE_PORT=${REMOTE_PORT:-22}
read -rp "Nom d'utilisateur distant : " REMOTE_USER
read -rp "Chemin absolu vers la clé SSH privée : " SSH_KEY_PATH

if [ ! -f "$SSH_KEY_PATH" ]; then
  echo "Erreur : La clé SSH privée n'existe pas à l'emplacement indiqué."
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

echo "Configuration enregistrée dans $ENV_FILE."
echo "Chargez ces variables avec : source $ENV_FILE"
