# RabbitMQ Email Consumer Service

This project is an asynchronous Python service that listens for messages on a RabbitMQ queue and sends emails based on the incoming message content. It supports configuration through environment variables and handles errors gracefully, making it robust and flexible for production use.

## Features
- **Asynchronous** message handling using `aio-pika` for RabbitMQ integration.
- **SMTP Email Sending** using the `smtplib` library.
- **Dynamic Configuration** via environment variables.
- **Graceful Shutdown** to handle interruptions and close connections safely.
- Supports different RabbitMQ exchange types (`direct`, `fanout`, `topic`, `headers`).

## Table of Contents
- [Getting Started](#getting-started)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Service](#running-the-service)
- [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

## Getting Started
Follow these instructions to set up the project on your local machine.

### Requirements
- Python 3.10+
- RabbitMQ Server
- Docker (optional, for containerized deployment)

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/rabbitmq-email-consumer.git
   cd rabbitmq-email-consumer

sudo docker build -t mail-service .

sudo docker run -d --network host --name myapp-mail-service \
  -e RABBITMQ_URL=amqp://admin:111111@localhost:5672/ \
  -e RABBITMQ_NAME=email_exchange \
  -e RABBITMQ_TYPE=direct \
  -e RABBITMQ_KEY=email_routing \
  -e RABBITMQ_QUEUE=email_queue \
  -e RABBITMQ_TTL=3600000 \
  -e SMTP_SERVER=smtp.mydomain.com \
  -e SMTP_PORT=587 \
  -e SMTP_USERNAME=abcd \
  -e SMTP_PASSWORD=1234 \
  -e SENDER_EMAIL=support@mydomain.com \
  mail-service

