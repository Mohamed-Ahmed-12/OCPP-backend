import json
from fastapi import FastAPI, HTTPException
import api.django_setup  # Load Django settings before importing models
from api.models import ChargePoint  # Import Django models
from ocpp.v16 import call
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

app = FastAPI()
channel_layer = get_channel_layer()


# Use async wrapper for database operations
@database_sync_to_async
def get_charger(charger_id):
    return ChargePoint.objects.filter(id=charger_id).first()

@database_sync_to_async
def is_charger_connected(charger_id):
    charger = ChargePoint.objects.filter(id=charger_id).first()
    return charger and charger.status=='available'

@app.post("/remote_start/{charger_id}")
async def remote_start_transaction(charger_id: str, id_tag: str = "default_tag" , connector_id: int = None):
    """
    Send a RemoteStartTransaction request to a specific charger.
    """
    charger = await get_charger(charger_id)  # ✅ Async-safe database call

    if not charger:
        raise HTTPException(status_code=404, detail="Charger not found")

    is_connected = await is_charger_connected(charger_id)
    if not is_connected:
        raise HTTPException(status_code=400, detail="Charger is not connected")
    
    try:
        # Create RemoteStartTransaction OCPP message
        request = call.RemoteStartTransaction(id_tag=id_tag)

        # Convert request to JSON properly
        request_json = json.dumps(request.__dict__)
        # Send request to Django Channels WebSocket Consumer
        await channel_layer.group_send(
            f"charger_{charger_id}",
            {"type": "remote.start","request": request_json,}
        )
        return {"status": "Remote Start Transaction Sent"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/remote_stop/{charger_id}')
async def remote_stop_transaction(charger_id: str ,transaction_id: int =121):
    """
    Send a RemoteStopTransaction request to a specific charger.
    """
    try:
        # Create RemoteStopTransaction OCPP message
        request = call.RemoteStopTransaction(transaction_id=transaction_id)
        # Convert request to JSON properly
        request_json = json.dumps(request.__dict__)
        # Send request to Django Channels WebSocket Consumer
        await channel_layer.group_send(
            f"charger_{charger_id}",
            {"type": "remote.stop","request": request_json,}
        )
        return {"status": "Remote Stop Transaction Sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))