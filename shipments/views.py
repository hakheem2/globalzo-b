from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Shipment
from django.conf import settings

def track_shipment_ajax(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request."}, status=400)

    tracking_number = request.GET.get("tracking_number", "").strip()

    if not tracking_number:
        return JsonResponse({"success": False, "message": "Enter a tracking number."}, status=400)

    shipment = Shipment.objects.filter(tracking_number__iexact=tracking_number).first()

    if not shipment:
        return JsonResponse({"success": False, "message": "Shipment not found."}, status=404)

    return JsonResponse({
        "success": True,
        "shipment": {
            "tracking_number": shipment.tracking_number,
            "status": shipment.get_status_display(),
            "current_location": shipment.current_location,
            "tracking_note": shipment.tracking_note,
            "estimated_delivery_date": shipment.estimated_delivery_date.strftime("%d %b %Y") if shipment.estimated_delivery_date else None,
        }
    })

def shipment_detail(request, tracking_number):
    shipment = get_object_or_404(
        Shipment.objects.prefetch_related("tracking_updates"),
        tracking_number__iexact=tracking_number
    )
    return render(request, "pages/shipment_detail.html", {
        "shipment": shipment,
        "MAPBOX_ACCESS_TOKEN": settings.MAPBOX_ACCESS_TOKEN,
    })