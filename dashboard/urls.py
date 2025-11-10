from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard_home"),
    path("export/csv/", views.export_dashboard_csv, name="dashboard_export_csv"),
]
