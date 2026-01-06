#!/bin/bash
# Configure PostgreSQL for remote access from specific IP

echo "=== Configuring PostgreSQL for Remote Access ==="
echo ""

# Backup pg_hba.conf
sudo cp /etc/postgresql/16/main/pg_hba.conf /etc/postgresql/16/main/pg_hba.conf.backup

# Add remote access for mcoder_app from your IP (114.4.83.255)
echo "# Allow mcoder_app from developer machine" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf
echo "host    mcoder_production    mcoder_app    114.4.83.255/32    md5" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf

# Also allow from any IP for development (optional - less secure)
# echo "host    mcoder_production    mcoder_app    0.0.0.0/0    md5" | sudo tee -a /etc/postgresql/16/main/pg_hba.conf

# Configure PostgreSQL to listen on all interfaces
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf
sudo sed -i "s/listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/16/main/postgresql.conf

# Restart PostgreSQL
sudo systemctl restart postgresql

echo ""
echo "✅ PostgreSQL configured for remote access"
echo "Allowed IP: 114.4.83.255"
echo ""
echo "Testing connection..."
sudo -u postgres psql -c "SELECT version();"

echo ""
echo "Done! Try connecting from local machine now."
