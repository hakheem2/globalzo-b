from django.db import models


class SiteSettings(models.Model):
   company_name = models.CharField(max_length=150, default="GlobalZo")
   email = models.EmailField(default="info@globalzologistics.com")
   phone = models.CharField(max_length=50, blank=True)
   address = models.CharField(max_length=255, blank=True)
   logo = models.ImageField(upload_to="site/", blank=True, null=True)

   updated_at = models.DateTimeField(auto_now=True)

   class Meta:
      verbose_name = "Site Settings"
      verbose_name_plural = "Site Settings"

   def __str__(self):
      return self.company_name