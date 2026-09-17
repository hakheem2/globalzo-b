from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings as django_settings

from shipments.models import Shipment
from core.models import SiteSettings
from .forms import SiteSettingsForm, ShipmentForm


def dashboard_login(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    error = None

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect("dashboard:home")
            error = "You do not have permission to access the dashboard."
        else:
            error = "Invalid username or password."

    return render(request, "dashboard/login.html", {"error": error})


@login_required
def dashboard_logout(request):
    logout(request)
    return redirect("dashboard:login")


@login_required
def dashboard(request):
    status_counts = Shipment.objects.values("status").annotate(total=Count("id"))
    counts = {item["status"]: item["total"] for item in status_counts}

    context = {
        "total_shipments": Shipment.objects.count(),
        "pending_shipments": counts.get("pending", 0),
        "in_transit_shipments": counts.get("in_transit", 0),
        "delivered_shipments": counts.get("delivered", 0),
        "recent_shipments": Shipment.objects.all()[:8],
    }

    return render(request, "dashboard/index.html", context)


@login_required
def shipments(request):
    shipments = Shipment.objects.all()

    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        shipments = shipments.filter(
            Q(tracking_number__icontains=search) |
            Q(sender_name__icontains=search) |
            Q(receiver_name__icontains=search)
        )

    if status:
        shipments = shipments.filter(status=status)

    return render(request, "dashboard/shipments.html", {
        "shipments": shipments,
        "search": search,
        "selected_status": status,
        "status_choices": Shipment.STATUS_CHOICES,
    })


@login_required
def customers(request):
    shipments = Shipment.objects.all()

    customers = {}

    for shipment in shipments:
        people = [
            (shipment.sender_name, shipment.sender_email, shipment.sender_phone),
            (shipment.receiver_name, shipment.receiver_email, shipment.receiver_phone),
        ]

        for name, email, phone in people:
            key = (name or "").strip().lower()

            if not key:
                continue

            if key not in customers:
                customers[key] = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "shipments": 0,
                }

            customers[key]["shipments"] += 1

    return render(request, "dashboard/customers.html", {
        "customers": customers.values(),
    })


@login_required
def reports(request):
    status_counts = Shipment.objects.values("status").annotate(total=Count("id"))
    method_counts = Shipment.objects.values("shipping_method").annotate(total=Count("id"))

    return render(request, "dashboard/reports.html", {
        "status_counts": status_counts,
        "method_counts": method_counts,
        "total_shipments": Shipment.objects.count(),
    })


@login_required
def users(request):
    return render(request, "dashboard/users.html", {
        "users": User.objects.all().order_by("username"),
    })



@login_required
def settings(request):
    site_settings = SiteSettings.objects.first()

    if not site_settings:
        site_settings = SiteSettings.objects.create()

    if request.method == "POST":
        form = SiteSettingsForm(request.POST, request.FILES, instance=site_settings)

        if form.is_valid():
            form.save()
            return redirect("dashboard:settings")
    else:
        form = SiteSettingsForm(instance=site_settings)

    return render(request, "dashboard/settings.html", {
        "form": form,
    })


@login_required
def shipment_add(request):
    if request.method == "POST":
        form = ShipmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("dashboard:shipments")
    else:
        form = ShipmentForm()

    return render(request, "dashboard/shipment_form.html", {
        "form": form,
        "MAPBOX_ACCESS_TOKEN": django_settings.MAPBOX_ACCESS_TOKEN,
        "page_title": "Add Shipment",
    })


@login_required
def shipment_edit(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == "POST":
        form = ShipmentForm(request.POST, instance=shipment)

        if form.is_valid():
            form.save()
            return redirect("dashboard:shipments")
    else:
        form = ShipmentForm(instance=shipment)

    return render(request, "dashboard/shipment_form.html", {
        "form": form,
        "MAPBOX_ACCESS_TOKEN": django_settings.MAPBOX_ACCESS_TOKEN,
        "page_title": "Edit Shipment",
        "shipment": shipment,
    })


@login_required
def shipment_delete(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == "POST":
        shipment.delete()

    return redirect("dashboard:shipments")