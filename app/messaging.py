import os
import json
from typing import Dict, Any, Optional
from aio_pika import connect_robust, Message, DeliveryMode
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue


# RabbitMQ configuration from environment variables (injected by docker-compose)
RABBITMQ_ENABLED = os.getenv("RABBITMQ_ENABLED", "true").lower() == "true"
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "admin")

RABBITMQ_URL = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@{RABBITMQ_HOST}/"

# Global connection and channel
connection: Optional[AbstractConnection] = None
channel: Optional[AbstractChannel] = None


async def init_rabbitmq():
    """Initialize RabbitMQ connection and channel"""
    global connection, channel
    
    if not RABBITMQ_ENABLED:
        print("RabbitMQ disabled - running in local mode")
        return
    
    try:
        connection = await connect_robust(RABBITMQ_URL)
        channel = await connection.channel()
        
        # Declare queues for consuming
        await channel.declare_queue("fincance-cadastro-funcionario-queue", durable=True) # Nova queue
        await channel.declare_queue("employee-deleted-queue", durable=True)
        await channel.declare_queue("employee-role-changed-queue", durable=True)
        
        # Declare queues for publishing (to ensure they exist)
        await channel.declare_queue("employee-paid-queue", durable=True)
        await channel.declare_queue("employee-dismissed-queue", durable=True)
        await channel.declare_queue("employee-status-changed-queue", durable=True)
        await channel.declare_queue("finance.expense.registered", durable=True)
        await channel.declare_queue("finance.expense.deleted", durable=True)
        
        print("RabbitMQ connection established")
    except Exception as e:
        print(f"Failed to connect to RabbitMQ: {e}")
        if RABBITMQ_ENABLED:
            print("RabbitMQ is enabled but connection failed. Continuing without RabbitMQ...")


async def close_rabbitmq():
    """Close RabbitMQ connection"""
    global connection
    if connection and not connection.is_closed:
        await connection.close()
        print("RabbitMQ connection closed")


async def publish_message(queue_name: str, message: Dict[str, Any]):
    """Publish message to RabbitMQ queue"""
    if not RABBITMQ_ENABLED:
        print(f"RabbitMQ disabled - would publish to {queue_name}: {message}")
        return
        
    if not channel:
        print(f"RabbitMQ not available - skipping message to {queue_name}: {message}")
        return
    
    try:
        # Ensure queue exists before publishing
        await channel.declare_queue(queue_name, durable=True)
        
        message_body = json.dumps(message)
        await channel.default_exchange.publish(
            Message(
                message_body.encode(),
                delivery_mode=DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )
        print(f"Message published to {queue_name}: {message}")
    except Exception as e:
        print(f"Failed to publish message to {queue_name}: {e}")


async def get_queue(queue_name: str) -> Optional[AbstractQueue]:
    """Get queue for consuming messages"""
    if not RABBITMQ_ENABLED or not channel:
        return None
    
    return await channel.declare_queue(queue_name, durable=True)
