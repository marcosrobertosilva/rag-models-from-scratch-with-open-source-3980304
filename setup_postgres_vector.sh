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

echo "=== Verifying installation ==="
su - postgres -c "psql -d text_embeddings -c \"\dx\" | grep vector"

EOFROOT

echo ""
echo "=== Setup complete! ==="
echo "Database: text_embeddings"
echo "Extension: vector"
echo ""
echo "To connect to the database, run:"
echo "sudo -u postgres psql -d text_embeddings"
