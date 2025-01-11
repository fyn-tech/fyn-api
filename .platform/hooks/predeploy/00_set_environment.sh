#!/bin/bash

# Create or modify the systemd service configuration
cat > /etc/systemd/system/web.service << 'EOL'
[Unit]
Description=This is web daemon
PartOf=eb-app.target

[Service]
User=webapp
Type=simple
# Key change: source the environment file before starting gunicorn
ExecStart=/bin/sh -c "source /opt/elasticbeanstalk/deployment/env && gunicorn --bind 127.0.0.1:8000 --workers=1 --threads=15 fyn-api.wsgi:application"
ExecStartPost=/bin/sh -c "systemctl show -p MainPID web.service | cut -d= -f2 > /var/pids/web.pid"
ExecStopPost=/bin/sh -c "rm -f /var/pids/web.pid"
Restart=always
SyslogIdentifier=web
WorkingDirectory=/var/app/current/

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and restart the web service
systemctl daemon-reload
systemctl restart web.service