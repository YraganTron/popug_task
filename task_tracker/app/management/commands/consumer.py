import json
import pika
import uuid
import random

from django.core.management.base import BaseCommand

from ...models import User, Task
from ...producer import Producer


def create_user(ch, method, properties, body):
    data = json.loads(body)
    user_data = data['data']
    User.objects.create(
        uuid=user_data['public_id'] or uuid.uuid4(),  # баг с публичным uuid
        username=user_data['email'],
        first_name=user_data['full_name'] or ''
    )


def reassign_tasks(ch, method, properties, body):
    data = json.loads(body)
    tasks = data['data']
    user_ids = User.objects.values_list('uuid', flat=True)  # только воркеры
    tasks = Task.objects.filter(uuid__in=tasks['task_ids'])
    for t in tasks:
        t.user = User.objects.get(uuid=random.choice(user_ids))
    Task.objects.bulk_update(tasks, ['user_id'])

    for t in tasks:
        event = {
            'event_name': 'Assigned Task',
            'event_version': 1,
            'data': {
                "uuid": t.uuid,
                "user_id": t.user_id,
            }
        }
        Producer().publish(event=event, exchange='task')


class Command(BaseCommand):
    help = 'Consume all event'

    def handle(self, *args, **kwargs):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='accounts-stream', exchange_type='fanout')
        channel.exchange_declare(exchange='task-shuffle', exchange_type='fanout')

        result_accounts = channel.queue_declare(queue='', exclusive=True)
        queue_name_accounts = result_accounts.method.queue
        result_task = channel.queue_declare(queue='', exclusive=True)
        queue_name_task = result_task.method.queue

        channel.queue_bind(exchange='accounts-stream', queue=queue_name_accounts)
        channel.queue_bind(exchange='task-shuffle', queue=queue_name_task)

        channel.basic_consume(queue=queue_name_accounts, on_message_callback=create_user, auto_ack=True)
        channel.basic_consume(queue=queue_name_task, on_message_callback=reassign_tasks, auto_ack=True)

        channel.start_consuming()
        # Ловить событие по изменению роли?
