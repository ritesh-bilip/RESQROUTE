from django.urls import path
from . import views

urlpatterns = [
    path('', views.control_center_map, name='map_dashboard'),
    path('api/map-data/', views.map_data_api, name='map_data_api'),
    path('api/report/', views.report_incident_api, name='report_incident_api'),
]