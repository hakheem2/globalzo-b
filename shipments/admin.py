from django import forms
from django.contrib import admin
from django.conf import settings
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Shipment, TrackingUpdate


class TrackingUpdateAdminForm(forms.ModelForm):
    class Meta:
        model = TrackingUpdate
        fields = (
            "status",
            "location",
            "latitude",
            "longitude",
            "note",
        )
        widgets = {
            "location": forms.TextInput(attrs={
                "id": "id_location",
                "autocomplete": "off",
            }),
            "latitude": forms.NumberInput(attrs={
                "id": "id_latitude",
                "step": "any",
                "readonly": True,
            }),
            "longitude": forms.NumberInput(attrs={
                "id": "id_longitude",
                "step": "any",
                "readonly": True,
            }),
        }


class ShipmentAdminForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = "__all__"
        widgets = {
            "origin": forms.TextInput(attrs={
                "id": "id_origin",
                "autocomplete": "off",
            }),
            "origin_latitude": forms.NumberInput(attrs={
                "id": "id_origin_latitude",
                "step": "any",
            }),
            "origin_longitude": forms.NumberInput(attrs={
                "id": "id_origin_longitude",
                "step": "any",
            }),
            "destination": forms.TextInput(attrs={
                "id": "id_destination",
                "autocomplete": "off",
            }),
            "destination_latitude": forms.NumberInput(attrs={
                "id": "id_destination_latitude",
                "step": "any",
            }),
            "destination_longitude": forms.NumberInput(attrs={
                "id": "id_destination_longitude",
                "step": "any",
            }),
        }


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):

    form = ShipmentAdminForm
    change_form_template = "admin/shipments/shipment_form.html"

    list_display = (
        "tracking_number",
        "sender_name",
        "receiver_name",
        "origin",
        "destination",
        "status",
        "shipping_method",
        "estimated_delivery_date",
        "created_at",
    )

    list_filter = (
        "status",
        "shipping_method",
        "package_type",
        "created_at",
    )

    search_fields = (
        "tracking_number",
        "sender_name",
        "sender_phone",
        "receiver_name",
        "receiver_phone",
        "origin",
        "destination",
    )

    readonly_fields = (
        "tracking_number",
        "current_location",
        "current_latitude",
        "current_longitude",
        "tracking_note",
        "tracking_history",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Tracking",
            {
                "fields": (
                    "tracking_number",
                    "status",
                    "current_location",
                    "current_latitude",
                    "current_longitude",
                    "tracking_note",
                    "tracking_history",
                )
            },
        ),
        (
            "Sender",
            {
                "fields": (
                    "sender_name",
                    "sender_phone",
                    "sender_email",
                    "sender_country",
                    "sender_city",
                    "sender_address",
                )
            },
        ),
        (
            "Receiver",
            {
                "fields": (
                    "receiver_name",
                    "receiver_phone",
                    "receiver_email",
                    "receiver_country",
                    "receiver_city",
                    "receiver_address",
                )
            },
        ),
        (
            "Shipping Route",
            {
                "fields": (
                    "origin",
                    "origin_latitude",
                    "origin_longitude",
                    "destination",
                    "destination_latitude",
                    "destination_longitude",
                )
            },
        ),
        (
            "Package Information",
            {
                "fields": (
                    "package_type",
                    "number_of_packages",
                    "weight",
                    "dimensions",
                    "description",
                )
            },
        ),
        (
            "Shipping Details",
            {
                "fields": (
                    "shipping_method",
                    "shipment_cost",
                    "estimated_delivery_date",
                )
            },
        ),
        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<path:object_id>/add-tracking-update/",
                self.admin_site.admin_view(self.add_tracking_update),
                name="shipments_shipment_add_tracking_update",
            ),
        ]

        return custom_urls + urls

    def add_tracking_update(self, request, object_id):
        shipment = get_object_or_404(Shipment, pk=object_id)

        if request.method == "POST":
            form = TrackingUpdateAdminForm(request.POST)

            if form.is_valid():
                tracking_update = form.save(commit=False)
                tracking_update.shipment = shipment
                tracking_update.save()

                self.message_user(
                    request,
                    "Tracking update added successfully."
                )

                return redirect(
                    reverse(
                        "admin:shipments_shipment_change",
                        args=[shipment.pk],
                    )
                )
        else:
            form = TrackingUpdateAdminForm()

        context = {
            **self.admin_site.each_context(request),
            "title": f"Add Tracking Update — {shipment.tracking_number}",
            "shipment": shipment,
            "form": form,
            "MAPBOX_ACCESS_TOKEN": settings.MAPBOX_ACCESS_TOKEN,
            "opts": self.model._meta,
            "has_view_permission": self.has_view_permission(
                request,
                shipment,
            ),
        }

        return render(
            request,
            "admin/shipments/add_tracking_update.html",
            context,
        )

    @admin.display(description="Tracking History")
    def tracking_history(self, obj):
        updates = obj.tracking_updates.all()

        add_url = reverse(
            "admin:shipments_shipment_add_tracking_update",
            args=[obj.pk],
        )

        if not updates:
            return mark_safe(
                f'''
                <div>
                    <a href="{add_url}" style="
                        display:inline-flex !important;
                        align-items:center !important;
                        gap:8px !important;
                        background:#0b6bcb !important;
                        color:#fff !important;
                        padding:11px 18px !important;
                        border-radius:6px !important;
                        border:0 !important;
                        text-decoration:none !important;
                        font-weight:600 !important;
                        font-size:14px !important;
                        margin-bottom:18px !important;
                        box-shadow:0 2px 5px rgba(11,107,203,.2) !important;
                    ">
                        <span style="font-size:18px !important;">+</span>
                        Add Tracking Update
                    </a>
                    <p style="color:#666;margin-top:15px;">No tracking updates yet.</p>
                </div>
                '''
            )

        rows = ""

        for update in updates:
            rows += f'''
                <tr>
                    <td style="padding:16px 18px; color:#aeaeae; font-weight:600; border-bottom:1px solid #edf1f5; white-space:nowrap;">
                        {update.get_status_display()}
                    </td>
                    <td style="padding:16px 18px; color:#aeaeae; border-bottom:1px solid #edf1f5;">
                        {update.location or "—"}
                    </td>
                    <td style="padding:16px 18px; color:#aeaeae; border-bottom:1px solid #edf1f5; white-space:nowrap;">
                        {update.created_at.strftime("%d %b %Y, %H:%M")}
                    </td>
                    <td style="padding:16px 18px; color:#aeaeae; border-bottom:1px solid #edf1f5; min-width:220px;">
                        {update.note or "No tracking note."}
                    </td>
                </tr>
            '''



        return mark_safe(f'''
        <div style="margin-top:8px;">
            <a href="{add_url}" style="display:inline-flex !important; align-items:center !important; gap:8px !important; background:#0b6bcb !important; color:#fff !important; padding:11px 18px !important; border-radius:6px !important; border:0 !important; text-decoration:none !important; font-weight:600 !important; font-size:14px !important; margin-bottom:22px !important;">
                <span style="font-size:18px;">+</span> Add Tracking Update
            </a>
            <div style="overflow-x:auto; border:1px solid #dfe6ee; border-radius:8px; background:#fff;">
                <table style="width:100%; border-collapse:collapse; margin:0;">
                    <thead>
                        <tr style="background:#102033;">
                            <th style="padding:15px 18px; text-align:left; color:#fff; font-size:14px; font-weight:600; border-right:1px solid rgba(255,255,255,.12);">Status</th>
                            <th style="padding:15px 18px; text-align:left; color:#fff; font-size:14px; font-weight:600; border-right:1px solid rgba(255,255,255,.12);">Location</th>
                            <th style="padding:15px 18px; text-align:left; color:#fff; font-size:14px; font-weight:600; border-right:1px solid rgba(255,255,255,.12);">Date & Time</th>
                            <th style="padding:15px 18px; text-align:left; color:#fff; font-size:14px; font-weight:600;">Note</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>
        ''')


    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        extra_context = extra_context or {}
        extra_context["MAPBOX_ACCESS_TOKEN"] = settings.MAPBOX_ACCESS_TOKEN

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )