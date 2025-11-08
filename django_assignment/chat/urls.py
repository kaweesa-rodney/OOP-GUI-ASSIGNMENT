from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.join_chatroom, name='join_chatroom'),
    path('room/<str:room_name>/<str:username>/', views.chatroom, name='chatroom'),
]