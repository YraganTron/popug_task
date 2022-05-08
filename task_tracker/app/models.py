import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)


class Task(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSE = 'close'
    TASK_STATUS_CHOICES = (
        (STATUS_OPEN, STATUS_OPEN),
        (STATUS_CLOSE, STATUS_CLOSE)
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, to_field='uuid', on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=TASK_STATUS_CHOICES, default=STATUS_OPEN)
