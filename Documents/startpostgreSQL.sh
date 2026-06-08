# Install PostgreSQL
sudo apt update && sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo pg_ctlcluster 16 main start

# Verify
sudo pg_ctlcluster 16 main status

# Enter PostgreSQL
sudo -u postgres psql

# Create database
CREATE DATABASE bankdb;

# Connect
\c bankdb

# Set password
\password postgres

# Exit
\q

# Test password login
PGPASSWORD=postgres psql -U postgres -h localhost -d bankdb