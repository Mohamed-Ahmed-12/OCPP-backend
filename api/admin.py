from django.contrib import admin
from .models import ChargePoint , Connector , Transaction , Messages
# Register your models here.
@admin.register(ChargePoint)
class ChargePointAdmin(admin.ModelAdmin):
    pass
@admin.register(Connector)
class ConnectorAdmin(admin.ModelAdmin):
    pass
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass
@admin.register(Messages)
class MessagesAdmin(admin.ModelAdmin):
    pass