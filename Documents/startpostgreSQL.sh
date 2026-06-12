#!/bin/bash

set -e

echo "====================================="
echo "Updating system packages..."
echo "====================================="
sudo apt update

echo "====================================="
echo "Installing Python and utilities..."
echo "====================================="
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python-is-python3 \
    git \
    curl \
    ca-certificates \
    gnupg

echo "====================================="
echo "Setting up Docker repository..."
echo "====================================="
sudo install -m 0755 -d /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) \
  signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "====================================="
echo "Installing Docker..."
echo "====================================="
sudo apt update

sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo "====================================="
echo "Configuring Docker permissions..."
echo "====================================="
sudo usermod -aG docker $USER

echo "====================================="
echo "Installing PostgreSQL..."
echo "====================================="
sudo apt install -y postgresql postgresql-contrib

PG_VERSION=$(psql --version | awk '{print $3}' | cut -d'.' -f1)

echo "Detected PostgreSQL version: $PG_VERSION"

sudo pg_ctlcluster "$PG_VERSION" main start
sudo pg_ctlcluster "$PG_VERSION" main status

echo "====================================="
echo "Configuring PostgreSQL..."
echo "====================================="

sudo -u postgres psql <<EOF
ALTER USER postgres WITH PASSWORD 'postgres';

SELECT 'Database already exists'
WHERE EXISTS (
    SELECT FROM pg_database WHERE datname = 'bankdb'
);

CREATE DATABASE bankdb
WITH OWNER postgres
TEMPLATE template0
ENCODING 'UTF8'
LOCALE_PROVIDER libc
CONNECTION LIMIT -1
IS_TEMPLATE FALSE;
EOF

echo "====================================="
echo "Verifying PostgreSQL connection..."
echo "====================================="

PGPASSWORD=postgres psql \
    -U postgres \
    -h localhost \
    -d bankdb \
    -c "SELECT version();"

echo "====================================="
echo "Installation Complete!"
echo "====================================="

echo ""
echo "Python:"
python --version

echo ""
echo "Docker:"
docker --version

echo ""
echo "Docker Compose:"
docker compose version

echo ""
echo "PostgreSQL:"
psql --version

echo ""
echo "IMPORTANT:"
echo "1. Log out and log back in for Docker group changes."
echo "2. PostgreSQL user: postgres"
echo "3. PostgreSQL password: postgres"
echo "4. Database: bankdb"