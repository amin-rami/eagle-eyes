from kafka import KafkaProducer
import json

from eagle_eyes.settings import KAFKA_BOOTSTRAP_SERVERS, KAFKA_EVENT_TOPIC


class KafkaStreamer:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KafkaStreamer, cls).__new__(cls)
            cls.instance.producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda msg: json.dumps(msg).encode('utf-8'),
                key_serializer=lambda key: key if key is None else str.encode(key)
            )
        return cls.instance

    def send(self, data: dict) -> None:
        key = data.get("user_id")
        self.producer.send(KAFKA_EVENT_TOPIC, key=key, value=data)


def get_streamer():
    return KafkaStreamer()
