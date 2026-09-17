from django.urls import path
from . import views

urlpatterns = [
    path("api/track/", views.track_shipment_ajax, name="track_shipment_ajax"),
    path("shipment/<str:tracking_number>/", views.shipment_detail, name="shipment_detail"),
]
