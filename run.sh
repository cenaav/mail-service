#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(cat .env | sed 's/#.*//g' | xargs)
fi

# Environment configuration
export RABBITMQ_URL="amqp://admin:si1992naAV@localhost:5672/"
export RABBITMQ_TYPE="direct"
export RABBITMQ_NAME="email_exchange"
export RABBITMQ_KEY="email_routing"
export RABBITMQ_QUEUE="email_queue"
export RABBITMQ_TTL=3600000
# Set email environment variables
export FROM_EMAIL="support@amonproject.com"
export SMTP_SERVER="smtp1.s.ipzmarketing.com"
export SMTP_PORT=587
export SMTP_USERNAME="dojmroxgaokw"
export SMTP_PASSWORD="dBcxr8F4-ZwE"

# Run the Python script
python3 r_read.py