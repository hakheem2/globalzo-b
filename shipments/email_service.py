import logging
import resend
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def get_recipients(shipment):
    recipients = []

    for email in [shipment.sender_email, shipment.receiver_email]:
        if email and email not in recipients:
            recipients.append(email)

    return recipients


def send_shipment_created_email(shipment):
    recipients = get_recipients(shipment)

    if not recipients:
        return

    html = render_to_string("emails/shipment_created.html", {
        "shipment": shipment,
        "site_url": settings.SITE_URL.rstrip("/"),
    })

    try:
        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": recipients,
            "subject": f"Shipment Created — {shipment.tracking_number}",
            "html": html,
        })
    except Exception:
        logger.exception("Failed to send shipment creation email.")


def send_shipment_status_email(shipment):
    recipients = get_recipients(shipment)

    if not recipients:
        return

    html = render_to_string("emails/shipment_status.html", {
        "shipment": shipment,
        "site_url": settings.SITE_URL.rstrip("/"),
    })

    try:
        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": recipients,
            "subject": f"Shipment Update — {shipment.tracking_number}",
            "html": html,
        })
    except Exception:
        logger.exception("Failed to send shipment status email.")