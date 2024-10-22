# file: email_producer.py
import aio_pika
import asyncio
import json
import os

# RabbitMQ configuration from environment variables
rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://admin:si1992naAV@127.0.0.1:5672/')
exchange_type = os.getenv('RABBITMQ_TYPE', 'direct')
exchange_name = os.getenv('RABBITMQ_NAME', 'email_exchange')
routing_key = os.getenv('RABBITMQ_KEY', 'email_routing')
queue_name = os.getenv('RABBITMQ_QUEUE', 'email_queue')
message_ttl = int(os.getenv('RABBITMQ_TTL', '3600000'))


async def send_email_message(subject, body, recipient_email):
    """Function to send an email message to the RabbitMQ queue."""
    # Establish a connection to RabbitMQ
    connection = await aio_pika.connect_robust(rabbitmq_url)
    
    async with connection:
        # Create a channel
        channel = await connection.channel()
        
        # Declare the exchange
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType.DIRECT, durable=True)
        
        # Create the email message as a dictionary
        email_message = {
            "to": recipient_email,
            "title": subject,
            "body": body
        }
        
        # Convert the dictionary to a JSON string
        message_body = json.dumps(email_message)
        
        # Publish the message to the exchange with the specified routing key
        await exchange.publish(
            aio_pika.Message(body=message_body.encode()),
            routing_key=routing_key  # Fix here, using 'routing_key' instead of 'email_routing_key'
        )
        
        print(f"Message sent to {routing_key} with body: {message_body}")

if __name__ == "__main__":

    # Example message content
    email_subject = "Welcome to the RabbitMQ Service"
    email_body = "Hello! This is a test message from your RabbitMQ email producer."
    recipient = "sina.av@gmail.com"

    # Run the async send_email_message function
    asyncio.run(send_email_message(email_subject, email_body, recipient))
