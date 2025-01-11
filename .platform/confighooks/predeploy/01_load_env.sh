#!/bin/bash

# Ensure the script runs with correct permissions
if [ -f /opt/elasticbeanstalk/deployment/env ]; then
    # Create a copy with correct permissions
    sudo cp /opt/elasticbeanstalk/deployment/env /opt/elasticbeanstalk/deployment/env.tmp
    sudo chown webapp:webapp /opt/elasticbeanstalk/deployment/env.tmp
    sudo chmod 644 /opt/elasticbeanstalk/deployment/env.tmp
    
    # Move the temp file to replace the original
    sudo mv /opt/elasticbeanstalk/deployment/env.tmp /opt/elasticbeanstalk/deployment/env
fi