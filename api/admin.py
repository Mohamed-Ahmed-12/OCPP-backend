from django.contrib import admin
from .models import ChargePoint
# Register your models here.
@admin.register(ChargePoint)
class ChargePointAdmin(admin.ModelAdmin):
    pass