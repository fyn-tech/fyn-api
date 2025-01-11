#!/bin/bash

# Debug: Print current environment variables
echo "Current environment variables:" > /tmp/env_debug.log
env >> /tmp/env_debug.log

# Debug: Check if env file exists and print its contents
echo "Contents of /opt/elasticbeanstalk/deployment/env:" >> /tmp/env_debug.log
cat /opt/elasticbeanstalk/deployment/env >> /tmp/env_debug.log

# Create or modify the systemd service configuration
cat > /etc/systemd/system/web.service << 'EOL'
[Unit]
Description=This is web daemon
PartOf=eb-app.target

[Service]
User=webapp
Type=simple
EnvironmentFile=/opt/elasticbeanstalk/deployment/env
ExecStart=/var/app/venv/staging-LQM1lest/bin/gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 fyn-api.wsgi:application
ExecStartPost=/bin/sh -c "systemctl show -p MainPID web.service | cut -d= -f2 > /var/pids/web.pid"
ExecStopPost=/bin/sh -c "rm -f /var/pids/web.pid"
Restart=always
SyslogIdentifier=web
WorkingDirectory=/var/app/current/

[Install]
WantedBy=multi-user.target
EOL

# Debug: Verify service file was created
echo "Contents of web.service:" >> /tmp/env_debug.log
cat /etc/systemd/system/web.service >> /tmp/env_debug.log

# Reload systemd
systemctl daemon-reload

# Debug: Check systemd status
systemctl status web >> /tmp/env_debug.log 2>&1