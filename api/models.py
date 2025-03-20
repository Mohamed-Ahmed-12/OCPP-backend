from django.db import models
import uuid

# Create your models here.
class ChargePoint(models.Model):
    """Represents a physical EV Charging Station."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255,help_text='latitude,longitude', null=True, blank=True)  # Optional Location
    status = models.CharField(max_length=20, choices=[
    ('available' , "Available"),
    ('preparing', "Preparing"),
    ('charging', "Charging"),
    ('suspended_evse' , "SuspendedEVSE"),
    ('suspended_ev' , "SuspendedEV"),
    ('finishing' , "Finishing"),
    ('reserved' , "Reserved"),
    ('unavailable' , "Unavailable"),
    ('faulted' , "Faulted"),
    ], default='available')
    max_power_kw = models.FloatField()  # Maximum power output in kW
    firmware_version = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChargePoint {self.charge_point_id} ({self.status})"



# status (e.g., completed, in-progress, failed)
class Transaction(models.Model):
    """Tracks ongoing and completed charging sessions"""
    charge_point_id = models.ForeignKey(ChargePoint, on_delete=models.CASCADE)
    connector_id = models.IntegerField()
    id_tag = models.CharField(max_length=100)  # RFID tag of the user
    meter_start = models.IntegerField()  # Energy level at the start (Wh)
    meter_stop = models.IntegerField(blank=True, null=True)  # Energy level at the end (Wh)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50,choices=[
        ('active','Active'),
        ('stopped','Stopped'),
    ] ,default="Active")

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"

class Messages(models.Model):
    """Used for debugging and monitoring charger activities."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    charge_point_id = models.ForeignKey(ChargePoint, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=100 , choices=[(1,'BootNotification'), (2,'StartTransaction')])  # BootNotification, StartTransaction, etc.
    payload = models.JSONField()  # Store full OCPP message as JSON
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.charge_point_id.id} - {self.message_type} ({self.timestamp})"
