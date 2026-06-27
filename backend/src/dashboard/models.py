from django.db import models

from tools.models import TimeStampedModel

# from users.models import Trader, Vehicle, Sub_Admin
# Create your models here.


class Location(TimeStampedModel):
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)

    class Meta:
        db_table = 'locations'
        unique_together = ['latitude', 'longitude']

class Branch(TimeStampedModel):
    title = models.CharField(max_length=40, unique=True, null=False, blank=False)
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='branches',
        null=False,
        blank=False
    )

    class Meta:
        db_table = 'branches'

class Audit_Logs(TimeStampedModel):
    sub_admin = models.ForeignKey(
        "users.Sub_Admin",
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=False,
        blank=False
    )
    action = models.CharField(max_length=65535, null=False, blank=False)

    class Meta:
        db_table = 'audit_logs'
