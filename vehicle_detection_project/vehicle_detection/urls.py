# vehicle_detection/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_video, name='upload_video'),
    path('status/<int:result_id>/', views.processing_status, name='processing_status'),
    path('results/', views.results_list, name='results_list'),
]