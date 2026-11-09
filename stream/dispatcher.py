import json
import os
import random
import ssl
import sys
import time
import pika

AMQP_URL = os.getenv("AMQP_URL")

if not AMQP_URL:
    print("[ERROR] AMQP_URL environment variable is not set!")
    print("Run this in PowerShell first:")
    print('$env:AMQP_URL = "amqps://user:pass@host/vhost"')
    sys.exit(1)

EXCHANGE_NAME = "rapido-dispatch"
CITIES = ["bangalore", "chennai"]
ZONES = ["koramangala", "indiranagar", "whitefield", "tnagar"]
TYPES = ["ride", "food"]

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
    print(f"[*] Dispatcher connected to CloudAMQP. Publishing to '{EXCHANGE_NAME}'...")

    msg_id = 1
    try:
        while True:
            city = random.choice(CITIES)
            zone = random.choice(ZONES)
            req_type = random.choice(TYPES)

            routing_key = f"{city}.{zone}.{req_type}"
            now_ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

            payload = {
                "id": f"REQ-{msg_id:04d}",
                "city": city,
                "type": req_type,
                "ts": now_ts
            }

            # Part D3 requirement: send 1 bad message every 10 messages
            is_bad = (msg_id % 10 == 0)
            if not is_bad:
                payload["zone"] = zone
            else:
                print(f"[!] Dispatching BAD message (missing 'zone'): id={payload['id']}")

            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            print(f"[+] Published #{msg_id} [{routing_key}]: {payload}")

            msg_id += 1
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping dispatcher...")
        connection.close()

if __name__ == "__main__":
    main()