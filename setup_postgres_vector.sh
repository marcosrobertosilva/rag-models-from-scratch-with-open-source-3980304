#!/bin/bash

# Script to install PostgreSQL, start service, and create text_embeddings database with vector extension

set -e  # Exit on error

# Run everything with sudo to avoid multiple password prompts
sudo bash << 'EOFROOT'
echo "=== Installing PostgreSQL ==="
apt-get update
apt-get install -y postgresql postgresql-contrib

echo "=== Starting PostgreSQL service ==="
service postgresql start

# Wait for PostgreSQL to be ready
echo "=== Waiting for PostgreSQL to be ready ==="
sleep 3

echo "=== Installing pgvector extension ==="
# Install build dependencies
apt-get install -y postgresql-server-dev-all git build-essential

# Clone and install pgvector
cd /tmp
if [ -d "pgvector" ]; then
    rm -rf pgvector
fi
git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

echo "=== Creating database and vector extension ==="
su - postgres -c "psql -c \"CREATE DATABASE text_embeddings;\" 2>/dev/null || echo 'Database may already exist'"
su - postgres -c "psql -d text_embeddings -c \"CREATE EXTENSION IF NOT EXISTS vector;\""

echo "=== Creating codespace user in PostgreSQL ==="
su - postgres -c "psql -c \"CREATE USER codespace WITH SUPERUSER;\" 2>/dev/null || echo 'User may already exist'"
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE text_embeddings TO codespace;\""

echo "=== Configuring authentication ==="
# Update pg_hba.conf to allow local connections without password
PG_VERSION=$(ls /etc/postgresql/)
PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"

# Backup original
cp "$PG_HBA" "${PG_HBA}.backup"

# Add trust authentication for local connections
sed -i 's/^local\s\+all\s\+all\s\+peer/local   all             all                                     trust/' "$PG_HBA"
sed -i 's/^host\s\+all\s\+all\s\+127.0.0.1\/32\s\+scram-sha-256/host    all             all             127.0.0.1\/32            trust/' "$PG_HBA"
sed -i 's/^host\s\+all\s\+all\s\+::1\/128\s\+scram-sha-256/host    all             all             ::1\/128                 trust/' "$PG_HBA"

echo "=== Restarting PostgreSQL service ==="
service postgresql restart
sleep 2

echo "=== Verifying installation ==="
su - postgres -c "psql -d text_embeddings -c \"\dx\" | grep vector"

EOFROOT

echo ""
echo "=== Setup complete! ==="
echo "Database: text_embeddings"
echo "Extension: vector"
echo "User: codespace (with superuser privileges)"
echo ""
echo "To connect to the database (no sudo needed), run:"
echo "psql -d text_embeddings"
