from dataclasses import asdict
import api.django_setup # Load Django settings before importing models
import json
import logging
from datetime import datetime, timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from ocpp.routing import on
from ocpp.v16 import call_result , call
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import RegistrationStatus
from ocpp.messages import CallResult
from api.models import Messages , ChargePoint , Connector , Transaction
logger = logging.getLogger(__name__)

class OCPPConsumer(AsyncWebsocketConsumer , cp):
    """OCPP Central System Management Server (CSMS)"""
    
    @database_sync_to_async
    def get_charger(self, charger_id):
        return ChargePoint.objects.filter(id=charger_id).first()
    
    async def connect(self):
        """ Handle new Charge Point WebSocket connection """
        self.charger_id = self.scope["url_route"]["kwargs"]["charger_id"]
        self.charge_point = await self.get_charger(self.charger_id)
            
        if not self.charge_point:
            logger.error(f"❌ Charger {self.charger_id} not found in the database.")
            await self.close()
            return
        # Explicitly initialize ChargePoint (cp) properly
        cp.__init__(self, self.charger_id, self )
        await self.accept()
        await self.channel_layer.group_add(f"charger_{self.charger_id}", self.channel_name)
        logger.info(f"🔌 Added {self.charger_id} to WebSocket group: charger_{self.charger_id}")
        logger.info(f"🔌 Charger {self.charger_id} connected")
    
    async def receive(self, text_data):
        """Handles incoming OCPP messages."""
        logger.info(f'Data {text_data}')
        try:
            data = json.loads(text_data) # text_data is list 
            message_type = data[2] if len(data) > 2 else "Unknown"
            # save the incoming request from cp (client side)
            logger.info(f'text_data {type(text_data)}')
            await self.save_message(charge_point=self.charge_point , message_type = message_type , payload = text_data)
            response = await self.route_message(text_data)
            logger.info(f'{response}')
            if response is not None:
                if isinstance(response, CallResult):
                    response_data = response.to_json()  # ✅ Correct way to serialize CallResult
                elif hasattr(response, "to_json"):
                    response_data = response.to_json()
                elif isinstance(response, dict):
                    response_data = json.dumps(response)
                else:
                    response_data = json.dumps(response.__dict__)  # Convert object attributes to JSON

                # Logging for debugging
                logger.info(f"Serialized response: {response_data}")

                # Save response to the database
                await self.save_message(charge_point=self.charge_point,  message_type=message_type, payload=response_data)
                
                # Send response back to client
                await self.send(response_data)  # ✅ Already in JSON format
        except Exception as e:
            logger.error(f"❌ Error processing message from {self.charger_id}: {e}", exc_info=True)
            await self.send(json.dumps({"error": "Invalid request"}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f"charger_{self.charger_id}", self.channel_name)
        logger.info(f"🚫 Charger {self.charger_id} disconnected")
    
    async def remote_start(self, event):
        """Handle RemoteStartTransaction request from FastAPI """
        logger.info(f"📩 Received Remote Start request: {event}")

        try:
            request_data = json.loads(event["request"])
            request = call.RemoteStartTransaction(**request_data)

            # Send the OCPP command to the charge point
            response = await self.call(request)

            logger.info(f"✅ Remote Start Response from CP: {response}")

            # Send response back to FastAPI
            return response
        except Exception as e:
            logger.error(f"❌ Error in remote_start: {e}")
            
    async def remote_stop(self,event):
        """Handle RemoteStopTransaction request from FastAPI """
        logger.info(f"📩 Received Remote Stop request: {event}")
        try:
            request_data = json.loads(event["request"])
            request = call.RemoteStopTransaction(**request_data)
            # Send the OCPP command to the charge point
            response = await self.call(request)
            logger.info(f"✅ Remote Stop Response from CP: {response}")
            # Send response back to FastAPI
            return response
        except Exception as e:
            logger.error(f"❌ Error in remote_stop: {e}")
            
    @on("BootNotification")
    async def on_boot_notification(self, charge_point_model, **kwargs):
        try:
            logger.info(f"🚀 Charger {self.charger_id} sent BootNotification: {charge_point_model}")
            response = call_result.BootNotification(
                current_time=datetime.now(timezone.utc).isoformat(),
                interval=60,
                status=RegistrationStatus.accepted  # Correct enum usage
            )
            logger.info(f"✅ Returning BootNotification response: {response}")
            return response
        except Exception as e:
            logger.error(f"❌ Error in on_boot_notification: {e}")
            return None  # Explicitly return None if an error occurs
        
    @on("Authorize")
    async def on_authorize(self, id_tag, **kwargs):
        """ Handle 'Authorize' request from Charge Point """
        logger.info(f"🔒 Charger {self.charger_id} sent Authorize: {id_tag}")
        return call_result.Authorize(
            id_tag_info={"status":"Accepted"}
            )

    @on("StartTransaction")
    async def on_start_transaction(self,id_tag,connector_id, meter_start,timestamp ,**kwargs):
        logger.info(f"⚡ Charger {self.charger_id} started a transaction")
        return call_result.StartTransaction(transaction_id=1,id_tag_info={"status":"Accepted"})
    
    @on("MeterValues")
    async def on_meter_values(self,connector_id,meter_value,transaction_id=None ,**kwargs):
        """ Handle 'MeterValues' request from Charge Point """
        logger.info(f"⚡ MeterValues received for transaction {transaction_id}: {meter_value}")
        return call_result.MeterValues()

    @on("StopTransaction")
    async def on_stop_transaction(self,meter_stop , timestamp , transaction_id , reason=None , id_tag=None,transaction_data=None,**kwargs):
        """ Handle 'StopTransaction' request from Charge Point """
        logger.info(f"⚡ Charger {self.charger_id} stopped a transaction")
        return call_result.StopTransaction(
            id_tag_info={"status":"Accepted"}
        )
        
    @on('Heartbeat')
    async def on_heartbeat(self, **kwargs):
        """ Handle 'Heartbeat' request from Charge Point """
        logger.info(f"⏱ Charger {self.charger_id} sent Heartbeat")
        return call_result.Heartbeat(
            current_time=datetime.now(timezone.utc).isoformat()
        )
        
    # Database operation
    @database_sync_to_async
    def save_message(self,charge_point, message_type, payload):
        """Save incoming OCPP messages to the database."""
        return Messages.objects.create(
            charge_point=charge_point,
            message_type=message_type,
            payload=payload
        )
