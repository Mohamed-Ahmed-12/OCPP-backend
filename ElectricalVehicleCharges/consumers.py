import json
import logging
from datetime import datetime, timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from ocpp.routing import on
from ocpp.v16 import call_result
from ocpp.v16 import ChargePoint as cp

logger = logging.getLogger(__name__)

class OCPPConsumer(AsyncWebsocketConsumer , cp):
    """OCPP Central System Management Server (CSMS)"""
    async def connect(self):
        self.charger_id = self.scope["url_route"]["kwargs"]["charger_id"]
        # Explicitly initialize ChargePoint (cp) properly
        cp.__init__(self, self.charger_id, self )
        
        await self.accept()
        print(f"🔌 Charger {self.charger_id} connected")
        await self.send(text_data=json.dumps({"message": f"Connected to charger {self.charger_id}"}))
    
    async def receive(self, text_data):
        """Handles incoming OCPP messages."""
        logger.info(f'Data {text_data} with type {type(text_data)}')
        try:
            response = await self.route_message(text_data)
            if response:
                await self.send(json.dumps(response))  # Convert response to JSON before sending
        except Exception as e:
            logger.error(f"❌ Error processing message from {self.charger_id}: {e}")
            await self.send(json.dumps({"error": "Invalid request"}))

    async def disconnect(self, close_code):
        print(f"🚫 Charger {self.charger_id} disconnected")

    @on("BootNotification")
    async def on_boot_notification(self, charge_point_model, **kwargs):
        print(f"🚀 Charger {self.charger_id} sent BootNotification: {charge_point_model}")
        return call_result.BootNotification(
            status="Accepted", current_time=datetime.now(timezone.utc).isoformat(), interval=10
        )
        
    @on("Authorize")
    async def on_authorize(self, id_tag, **kwargs):
        """ Handle 'Authorize' request from Charge Point """
        print(f"🔒 Charger {self.charger_id} sent Authorize: {id_tag}")
        return call_result.Authorize(
            id_tag_info={"status":"Accepted"}
            )

    @on("StartTransaction")
    async def on_start_transaction(self,id_tag,connector_id, meter_start,timestamp ,**kwargs):
        print(f"⚡ Charger {self.charger_id} started a transaction")
        return call_result.StartTransaction(transaction_id=1,id_tag_info={"status":"Accepted"})
    
    @on("MeterValues")
    async def on_meter_values(self,connector_id,meter_value,transaction_id=None ,**kwargs):
        """ Handle 'MeterValues' request from Charge Point """
        print(f"⚡ MeterValues received for transaction {transaction_id}: {meter_value}")
        return call_result.MeterValues()

    @on("StopTransaction")
    async def on_stop_transaction(self,meter_stop , timestamp , transaction_id , reason=None , id_tag=None,transaction_data=None,**kwargs):
        """ Handle 'StopTransaction' request from Charge Point """
        print(f"⚡ Charger {self.charger_id} stopped a transaction")
        return call_result.StopTransaction(
            id_tag_info={"status":"Accepted"}
        )
        