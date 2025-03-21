import os
import django

# Set the environment variable for Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ElectricalVehicleCharges.settings")

# Initialize Django
django.setup()