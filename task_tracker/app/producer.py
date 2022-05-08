import pika
import json
import uuid
import datetime


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class Producer(metaclass=Singleton):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.producer = 'task_tracker'

    def publish(self, event, exchange):
        event.update({"event_id": uuid.uuid4(), "event_time": datetime.datetime.utcnow().isoformat()})
        channel = self.connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='fanout')
        channel.basic_publish(exchange=exchange, routing_key='', body=json.dumps(event, cls=UUIDEncoder))
