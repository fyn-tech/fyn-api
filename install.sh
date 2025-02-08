#!/bin/bash

echo "Installing PostgreSQL..."
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql