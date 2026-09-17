from django import forms
from core.models import SiteSettings

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["company_name", "email", "phone", "address", "logo"]
        widgets = {
            "company_name": forms.TextInput(attrs={"placeholder": "Company name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone number"}),
            "address": forms.TextInput(attrs={"placeholder": "Company address"}),
        }


from shipments.models import Shipment

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            "sender_name", "sender_phone", "sender_email",
            "sender_country", "sender_city", "sender_address",
            "receiver_name", "receiver_phone", "receiver_email",
            "receiver_country", "receiver_city", "receiver_address",
            "package_type", "number_of_packages", "weight",
            "dimensions", "description",
            "origin", "origin_latitude", "origin_longitude",
            "destination", "destination_latitude", "destination_longitude",
            "current_location", "current_latitude", "current_longitude",
            "shipping_method", "shipment_cost", "estimated_delivery_date",
            "status", "tracking_note",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "tracking_note": forms.Textarea(attrs={"rows": 3}),
            "estimated_delivery_date": forms.DateInput(attrs={"type": "date"}),
            "weight": forms.NumberInput(attrs={
                "placeholder": "Enter weight (kg, g, or lb)"
            }),
            "dimensions": forms.TextInput(attrs={
                "placeholder": "Enter dimensions (cm, m, or mm)"
            }),
            "origin_latitude": forms.HiddenInput(),
            "origin_longitude": forms.HiddenInput(),
            "destination_latitude": forms.HiddenInput(),
            "destination_longitude": forms.HiddenInput(),
            "current_latitude": forms.HiddenInput(),
            "current_longitude": forms.HiddenInput(),
        }