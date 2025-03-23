# OCPP Backend Module for Electric Vehicle (EV) Chargers

## Overview
This backend module facilitates communication between the backend system and EV chargers using the **OCPP 1.6 JSON** protocol over **WebSockets**. It enables remote management of chargers, transaction monitoring, and real-time status updates.

## System Setup

### Clone and Navigate to the Project
```sh
git clone https://github.com/Mohamed-Ahmed-12/OCPP-backend.git
cd ElectricalVehicleCharges
```

### Running the Server Side
```sh
docker-compose up --build -d
```

### Running the Client Side
```sh
docker exec -it evcharges_backend bash
cd ElectricalVehicleCharges
python charge_point_client.py
```

## Testing & Debugging

### Using Postman WebSocket Requests
- Send WebSocket requests to test charger communication.
- Validate message responses for different OCPP actions.

### Using an OCPP Simulator
1. Install the OCPP ChargeStation simulator.
2. Connect to the WebSocket server:
   ```sh
   python charge_point_client.py
   ```
3. Verify responses and API interactions.

## API Endpoints
**Base URL:** `ws://localhost:8000/ws/evcharger/{charger_id}/`

| Endpoint                        | Method   | Description                                               |
|---------------------------------|----------|-----------------------------------------------------------|
| `/ws/evcharger/{charger_id}/`   | WebSocket | Connects an EV charger to the backend via WebSocket.     |
| `/chargers`                     | GET      | Lists all connected chargers.                            |
| `/start/{charger_id}`           | POST     | Sends a remote start command to the charger.             |
| `/stop/{charger_id}`            | POST     | Sends a remote stop command to the charger.              |

## Technology Stack
- **Docker**: Builds, deploys, runs, updates, and manages the application.
- **Postman**: Used to send and test WebSocket requests.
- **Django**: Core backend framework for handling the database, authentication, and session management.
- **Django Channels**: Extends Django to support WebSockets for real-time communication.
- **FastAPI**: Used to build API endpoints.
- **WebSockets**: Enables real-time communication with EV chargers.
- **OCPP Library**: Provides the necessary building blocks to implement an OCPP charging station and central system.
- **Daphne**: HTTP, HTTP2, and WebSocket server for Django Channels.
- **Uvicorn**: ASGI web server for FastAPI.
- **PostgreSQL**: Stores charger and transaction data.

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, please reach out to the project maintainers.
