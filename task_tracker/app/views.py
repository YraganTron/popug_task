from django.http import Http404

from rest_framework import permissions, viewsets, views, status, generics
from rest_framework.response import Response


from .models import Task, User
from .serializers import TaskSerializer, TaskCloseSerializer
from .producer import Producer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, queryset):
        queryset = queryset.filter(user_id=self.request.user.uuid, status=Task.STATUS_OPEN)
        return queryset

    def perform_create(self, serializer):
        obj = serializer.save(user=User.objects.order_by('?')[0])
        event = {
            'event_name': 'Task Created',
            'event_version': 1,
            'data': {
                "uuid": obj.uuid,
                "user_id": obj.user_id,
                "description": obj.description,
                "status": obj.status,
            }
        }
        Producer().publish(event=event, exchange='task-streaming')

        event = {
            'event_name': 'Assigned Task',
            'event_version': 1,
            'data': {
                "uuid": obj.uuid,
                "user_id": obj.user_id,
            }
        }
        Producer().publish(event=event, exchange='task-billing')

    def destroy(self, request, *args, **kwargs):
        raise Http404


class TaskReassigns(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task_ids = Task.objects.filter(status=Task.STATUS_OPEN).values_list('uuid', flat=True)
        event = {
            'event_name': 'Shuffled Tasks',
            'event_version': 1,
            'data': {
                'task_ids': list(task_ids)
            }
        }
        Producer().publish(event=event, exchange='task-shuffle')
        return Response(status=status.HTTP_200_OK)


class TaskClose(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCloseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        obj = serializer.save()
        event = {
            'event_name': 'Closed Task',
            'event_version': 1,
            'data': {
                "uuid": obj.uuid,
                "status": obj.status,
            }
        }
        Producer().publish(event=event, exchange='task-billing')
