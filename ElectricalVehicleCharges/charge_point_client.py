# how run this py module 
# docker exec -it evcharges_backend bash (then) python charge_point.py

import asyncio
import websockets
import logging
from datetime import datetime , timezone 
from ocpp.v16 import call
from ocpp.v16 import ChargePoint as cp
from ocpp.routing import on

logger = logging.getLogger(__name__)

class ChargePointClient(cp):
    """ Charge Point """
    async def send_boot_notification(self):
        """ Send BootNotification to the OCPP Server (CSMS) """
        request = call.BootNotification(
            charge_point_model="EVSE-123",
            charge_point_vendor="EV-Charger Inc."
        )
        response = await self.call(request)
        print(f'📡 BootNotification Response: {response}')

    async def send_authorize(self, id_tag):
        """ Send Authorize request """
        request = call.Authorize(id_tag=id_tag)
        response = await self.call(request)
        print(f"🔒 Authorize Response: {response}")

    async def send_start_transaction(self, id_tag, connector_id):
        """ Send StartTransaction request """
        request = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=0,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        response = await self.call(request)
        print(f"⚡ StartTransaction Response: {response}")

    async def send_stop_transaction(self, transaction_id):
        """ Send StopTransaction request """
        request = call.StopTransaction(
            transaction_id=transaction_id,
            meter_stop=100,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason="Local"
        )
        response = await self.call(request)
        print(f"🚫 StopTransaction Response: {response}")

    async def send_heartbeat(self):
        """ Send Heartbeat request """
        while True:
            request = call.Heartbeat()
            response = await self.call(request)
            print(f"⏱ Heartbeat Response: {response}")
            await asyncio.sleep(60)
    
async def connect_to_server():
    uri = "ws://localhost:8000/ws/evcharger/cfcf351e-47ed-4e9a-93b1-62d2ce26d550/"  

    try:
        async with websockets.connect(uri) as ws:
            charge_point = ChargePointClient("EVSE-123", ws)
            
            # Start listening for incoming messages
            listener_task = asyncio.create_task(charge_point.start())  
            await asyncio.sleep(2)  # Give time for connection setup

            # ✅ Step 1: Send Boot Notification (Initial Registration)
            await charge_point.send_boot_notification()

            # ✅ Step 2: Start Heartbeat in Background
            heartbeat_task = asyncio.create_task(charge_point.send_heartbeat())

            # ✅ Step 3: Authorize the User
            await asyncio.sleep(2)  # Small delay before authorization
            await charge_point.send_authorize("123456")

            # ✅ Step 4: Start Charging Transaction
            await asyncio.sleep(2)  # Ensure authorization is completed
            await charge_point.send_start_transaction("123456", 1)  

            # ✅ Step 5: Simulate Charging (wait time)
            await asyncio.sleep(10)  # Simulating a charging session

            # ✅ Step 6: Stop the Charging Transaction
            await charge_point.send_stop_transaction(transaction_id=1)

            # ✅ Cleanup: Stop heartbeat and WebSocket listener
            heartbeat_task.cancel()
            listener_task.cancel()

            try:
                await heartbeat_task
                await listener_task
            except asyncio.CancelledError:
                logger.info("🛑 Tasks stopped gracefully.")

    except websockets.exceptions.ConnectionClosedOK:
        logger.info("✅ WebSocket connection closed normally.")

    except Exception as e:
        logger.error(f"❌ WebSocket Error: {e}")

if __name__ == "__main__":
    asyncio.run(connect_to_server())

