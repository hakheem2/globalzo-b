from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.dashboard_login, name="login"),
    path("logout/", views.dashboard_logout, name="logout"),

    path("", views.dashboard, name="home"),
    path("shipments/", views.shipments, name="shipments"),
    path("customers/", views.customers, name="customers"),
    path("reports/", views.reports, name="reports"),
    path("users/", views.users, name="users"),
    path("settings/", views.settings, name="settings"),

    path("shipments/add/", views.shipment_add, name="shipment_add"),
    path("shipments/<int:pk>/edit/", views.shipment_edit, name="shipment_edit"),
    path("shipments/<int:pk>/delete/", views.shipment_delete, name="shipment_delete"),
]