from django.urls import path, include

from rest_framework import routers

from .views import TaskViewSet, TaskReassigns, TaskClose

router = routers.DefaultRouter()
router.register(r'task', TaskViewSet)

urlpatterns = [
    path('task/reassigns/', TaskReassigns.as_view()),
    path('task/<int:pk>/close/', TaskClose.as_view()),
    path('', include(router.urls)),
]
