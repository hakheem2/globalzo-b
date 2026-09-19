from django.db import models
from django.utils.crypto import get_random_string

from .email_service import send_shipment_created_email, send_shipment_status_email


class Shipment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("picked_up", "Picked Up"),
        ("in_transit", "In Transit"),
        ("at_destination", "At Destination"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("delayed", "Delayed"),
        ("cancelled", "Cancelled"),
    ]

    SHIPPING_METHOD_CHOICES = [
        ("express", "Express Shipping"),
        ("standard", "Standard Shipping"),
    ]

    PACKAGE_TYPE_CHOICES = [
        ("document", "Document"),
        ("parcel", "Parcel"),
        ("box", "Box"),
        ("cargo", "Cargo"),
        ("other", "Other"),
    ]

    tracking_number = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    # Sender
    sender_name = models.CharField(max_length=150)
    sender_phone = models.CharField(max_length=50)
    sender_email = models.EmailField(blank=True)
    sender_country = models.CharField(max_length=100)
    sender_city = models.CharField(max_length=100)
    sender_address = models.CharField(max_length=255)

    # Receiver
    receiver_name = models.CharField(max_length=150)
    receiver_phone = models.CharField(max_length=50)
    receiver_email = models.EmailField(blank=True)
    receiver_country = models.CharField(max_length=100)
    receiver_city = models.CharField(max_length=100)
    receiver_address = models.CharField(max_length=255)

    # Package
    package_type = models.CharField(
        max_length=30,
        choices=PACKAGE_TYPE_CHOICES
    )
    number_of_packages = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    dimensions = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Route
    origin = models.CharField(max_length=255)
    origin_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    origin_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    destination = models.CharField(max_length=255)
    destination_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    destination_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )

    # Shipping
    shipping_method = models.CharField(
        max_length=20,
        choices=SHIPPING_METHOD_CHOICES
    )
    shipment_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    estimated_delivery_date = models.DateField(
        null=True,
        blank=True
    )

    # Tracking
    current_location = models.CharField(
        max_length=255,
        blank=True
    )
    current_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="pending"
    )
    tracking_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None

        if not is_new:
            old_status = Shipment.objects.filter(pk=self.pk).values_list("status", flat=True).first()

        if not self.tracking_number:
            self.tracking_number = f"GZ-{get_random_string(10).upper()}"

        super().save(*args, **kwargs)

        if is_new:
            send_shipment_created_email(self)
        elif old_status != self.status: 
            send_shipment_status_email(self)

    def __str__(self):
        return self.tracking_number


class TrackingUpdate(models.Model):
    shipment = models.ForeignKey(
        Shipment,
        on_delete=models.CASCADE,
        related_name="tracking_updates"
    )

    status = models.CharField(
        max_length=30,
        choices=Shipment.STATUS_CHOICES
    )
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        shipment = self.shipment
        shipment.status = self.status
        shipment.current_location = self.location
        shipment.current_latitude = self.latitude
        shipment.current_longitude = self.longitude
        shipment.tracking_note = self.note
        shipment.save(
            update_fields=[
                "status",
                "current_location",
                "current_latitude",
                "current_longitude",
                "tracking_note",
                "updated_at",
            ]
        )

    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.get_status_display()}"