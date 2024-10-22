import os
import time
import re
import json
import signal
import asyncio
import aio_pika
from email_utils import EmailSender


# Email validation regex pattern
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


# RabbitMQ variables from environment
rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://admin:si1992naAV@localhost:5672/')
exchange_type = os.getenv('RABBITMQ_TYPE', 'direct')
exchange_name = os.getenv('RABBITMQ_NAME', 'email_exchange')
routing_key = os.getenv('RABBITMQ_KEY', 'email_routing')
queue_name = os.getenv('RABBITMQ_QUEUE', 'email_queue')
message_ttl = int(os.getenv('RABBITMQ_TTL', '3600000'))

# Email configuration
smtp_server = os.getenv('SMTP_SERVER', "smtp1.s.ipzmarketing.com")
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_username = os.getenv('SMTP_USERNAME', "dojmroxgaokw")
smtp_password = os.getenv('SMTP_PASSWORD', "dBcxr8F4-ZwE")
sender_email = os.getenv('SENDER_EMAIL', "support@amonproject.com")


# Create a persistent EmailSender instance
email_sender = EmailSender(smtp_server, smtp_port, smtp_username, smtp_password, sender_email)


def is_valid_email(email):
    """Validate email address using regex."""
    return bool(EMAIL_REGEX.match(email))


async def connect_to_rabbitmq():
    """Connect to RabbitMQ with a retry mechanism."""
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            connection = await aio_pika.connect_robust(rabbitmq_url)
            channel = await connection.channel()
            print("RabbitMQ connection established.")
            return connection, channel
        except aio_pika.exceptions.AMQPConnectionError as e:
            retries += 1
            wait_time = min(2 ** retries, 30)  # Exponential backoff
            print(f"RabbitMQ connection failed. Retrying in {wait_time} seconds... (Attempt {retries}/{max_retries})")
            await asyncio.sleep(wait_time)

    raise Exception("Failed to connect to RabbitMQ after several attempts.")


async def main():
    connection, channel = await connect_to_rabbitmq()
    if connection and channel:
        # Proceed with queue and exchange declarations
        exchange = await channel.declare_exchange(exchange_name, aio_pika.ExchangeType(exchange_type), durable=True)
        queue = await channel.declare_queue(queue_name, durable=True, exclusive=False, auto_delete=False)
        await queue.bind(exchange, routing_key)
        await queue.consume(on_message)

        print(f"Listening on {queue_name} for email tasks with routing key '{routing_key}'...")
        return channel, connection
    else:
        print("Failed to establish RabbitMQ connection.")
        return None, None


async def on_message(message: aio_pika.IncomingMessage):
    """Process received RabbitMQ message."""
    try:
        # Decode message body from bytes to string
        body = message.body.decode('utf-8')

        # Print the type of the message body and content for debugging
        # print(f"Raw message body: {message.body}")
        # print(f"Decoded message body: {body}")
        # print(f"Type of decoded message: {type(body)}")

        # Deserialize the string to a Python dictionary if it's a valid JSON string
        try:
            email_task = json.loads(body)
            # print(f"Deserialized email task: {email_task}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            await message.reject(requeue=False)
            return

        # Ensure email_task is a dictionary
        if isinstance(email_task, str):
            try:
                email_task = json.loads(email_task)
                # print(f"Deserialized email task: {email_task}")
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                await message.reject(requeue=False)
                return

        # Ensure email_task is a dictionary
        if isinstance(email_task, dict):
            # Extract email fields from the task
            recipient_email = email_task.get("to")
            email_subject = email_task.get("title")
            email_body = email_task.get("body")

            # Validate email address format
            if not is_valid_email(recipient_email):
                print(f"Invalid email address format: {recipient_email}. Removing from queue.")
                await message.reject(requeue=False)
                return

            # Validate message content
            if not (recipient_email and email_subject and email_body):
                raise ValueError("Incomplete email data in the task")

            # Use the persistent EmailSender instance to send the email
            confirm = email_sender.send_email(email_subject, email_body, recipient_email)
            if confirm:
                print(f"Message successfully processed and acknowledged: {email_task}")
                await message.ack()
            else:
                print(f"Failed to send email, requeuing message: {email_task}")
                await message.reject(requeue=True)
        else:
            print(f"Message is not a dictionary: {email_task}")
            await message.reject(requeue=False)

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reject(requeue=True)


async def shutdown(signal, loop, channel, connection):
    """Cleanup tasks and connections on shutdown."""
    print(f"Received exit signal {signal.name}...")

    # Close the RabbitMQ channel and connection
    if channel:
        await channel.close()
        print("RabbitMQ channel closed.")
    if connection:
        await connection.close()
        print("RabbitMQ connection closed.")

    # Safely close the SMTP connection
    try:
        email_sender.close()
        print("SMTP connection closed.")
    except Exception as e:
        print(f"Error closing SMTP connection: {e}")

    # Cancel all outstanding tasks
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]

    print("Cancelling outstanding tasks...")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


if __name__ == "__main__":
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    channel, connection = None, None

    try:
        # Run the async main function
        channel, connection = loop.run_until_complete(main())

        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig, lambda sig=sig: asyncio.create_task(shutdown(sig, loop, channel, connection))
            )

        # Run the event loop until the loop is stopped
        loop.run_forever()
    finally:
        # Close resources on program exit
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        print("Asyncio event loop closed.")