from fastapi import FastAPI
import api.django_setup # Load Django settings before importing models
from .models import ChargePoint # Import Django models

app = FastAPI()

# Create your views here.
@app.get("/chargers")
def get_chargers():    
    chargers = ChargePoint.objects.filter(status__iexact ='available')
    return {"chargers": list(chargers)}


# Listing connected chargers.
# Sending remote start/stop commands.
# Fetching transaction logs.