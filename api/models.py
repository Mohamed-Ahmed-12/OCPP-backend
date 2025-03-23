from django.db import models
import uuid

class ChargePoint(models.Model):
    """Represents an EV Charging Station."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # Human-readable name
    location = models.CharField(max_length=255, help_text='latitude,longitude', null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # WebSocket connection IP
    is_online = models.BooleanField(default=False)  # Track online/offline state
    status = models.CharField(max_length=20, choices=[
        ('available', "Available"),
        ('preparing', "Preparing"),
        ('charging', "Charging"),
        ('suspended_evse', "SuspendedEVSE"),
        ('suspended_ev', "SuspendedEV"),
        ('finishing', "Finishing"),
        ('reserved', "Reserved"),
        ('unavailable', "Unavailable"),
        ('faulted', "Faulted"),
    ], default='available')
    max_power_kw = models.FloatField()  # Maximum power output in kW
    firmware_version = models.CharField(max_length=100, null=True, blank=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)  # Last heartbeat received
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    charge_point_model = models.CharField(max_length=250 , null=True , blank=True)
    charge_point_vendor = models.CharField(max_length=250 , null=True , blank=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Connector(models.Model):
    """Represents a charging connector within a ChargePoint."""
    charge_point = models.ForeignKey(ChargePoint, on_delete=models.CASCADE, related_name='connectors')
    type = models.CharField(max_length=50, choices=[
        ('Type1', 'Type 1'),
        ('Type2', 'Type 2'),
        ('CHAdeMO', 'CHAdeMO'),
        ('CCS', 'CCS'),
    ])
    max_current = models.FloatField()  # Maximum current in Amps
    voltage = models.FloatField(null=True, blank=True)  # Voltage level
    status = models.CharField(max_length=50, choices=[
        ('Available', 'Available'),
        ('Charging', 'Charging'),
        ('Faulted', 'Faulted'),
        ('Preparing', 'Preparing'),
        ('Reserved', 'Reserved'),
        ('Unavailable', 'Unavailable'),
    ])
    power_type = models.CharField(max_length=50, choices=[
        ('AC', 'AC'),
        ('DC', 'DC'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Connector {self.id} ({self.type}) - {self.charge_point.name}"


class Transaction(models.Model):
    """Tracks charging sessions."""
    charge_point = models.ForeignKey(ChargePoint, on_delete=models.CASCADE)
    connector = models.ForeignKey(Connector, on_delete=models.CASCADE)
    transaction_id = models.IntegerField(unique=True, null=True, blank=True)  # OCPP Transaction ID
    id_tag = models.CharField(max_length=100)  # RFID tag of the user
    meter_start = models.IntegerField()  # Start energy (Wh)
    meter_stop = models.IntegerField(blank=True, null=True)  # Stop energy (Wh)
    start_time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('stopped', 'Stopped'),
        ('failed', 'Failed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ], default="active")

    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"


class Messages(models.Model):
    """Logs OCPP messages for debugging and tracking."""
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    charge_point = models.ForeignKey(ChargePoint, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=50, choices=[
        ('BootNotification', 'BootNotification'),
        ('StartTransaction', 'StartTransaction'),
        ('StopTransaction', 'StopTransaction'),
        ('Heartbeat', 'Heartbeat'),
        ('Authorize', 'Authorize'),
        ('MeterValues','MeterValues'),
    ])
    payload = models.JSONField()  # Store full OCPP message as JSON
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.charge_point.name} - {self.message_type} ({self.timestamp})"
