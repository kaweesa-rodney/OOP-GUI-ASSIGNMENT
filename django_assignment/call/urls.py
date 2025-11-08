from django.urls import path
from . import views

app_name = 'call'

urlpatterns = [
    path('', views.index, name='index'),
]