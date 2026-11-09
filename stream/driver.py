import json
import os
import ssl
import sys
import pika

AMQP_URL = os.getenv("AMQP_URL")

if not AMQP_URL:
    print("[ERROR] AMQP_URL environment variable is not set!")
    print("Run this in PowerShell first:")
    print('$env:AMQP_URL = "amqps://user:pass@host/vhost"')
    sys.exit(1)

EXCHANGE_NAME = "rapido-dispatch"

if len(sys.argv) < 3:
    print("Usage: python driver.py <NAME> <PATTERN>")
    print("Example: python driver.py Ravi bangalore.koramangala.*")
    sys.exit(1)

DRIVER_NAME = sys.argv[1]
BINDING_PATTERN = sys.argv[2]

def on_message(ch, method, properties, body):
    routing_key = method.routing_key
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception:
        print(f"[{DRIVER_NAME}] Malformed JSON! (NACK)")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    # Part D3: basic_nack if missing zone, basic_ack otherwise
    if "zone" not in data or not data["zone"]:
        print(f"[{DRIVER_NAME}] REJECTED (NACK): missing zone in {data['id']} (key: {routing_key})")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"[{DRIVER_NAME}] ACCEPTED (ACK): {data['id']} in {data['zone']} ({data['type']}) key={routing_key}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

def get_connection(url: str):
    parameters = pika.URLParameters(url)
    if url.startswith("amqps://"):
        context = ssl.create_default_context()
        parameters.ssl_options = pika.SSLOptions(context)
    return pika.BlockingConnection(parameters)

def main():
    connection = get_connection(AMQP_URL)
    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=True)

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=BINDING_PATTERN)
    print(f"[{DRIVER_NAME}] Listening on '{BINDING_PATTERN}'...")

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=on_message)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"\n[{DRIVER_NAME}] Stopping...")
        channel.stop_consuming()
        connection.close()

if __name__ == "__main__":
    main()