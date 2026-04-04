# API Gateway Service

Centralized FastAPI gateway for routing requests to all backend microservices.

## Service URL

- http://localhost:8050

## Gateway Endpoints

- `GET /health`
- `GET /services`
- `ANY /api/patient`
- `ANY /api/patient/{path}`
- `ANY /api/doctor`
- `ANY /api/doctor/{path}`
- `ANY /api/appointment`
- `ANY /api/appointment/{path}`
- `ANY /api/notification`
- `ANY /api/notification/{path}`

The generic fallback routes (`/api/{service}` and `/api/{service}/{path}`) still work but are hidden from Swagger UI.

## Supported service keys

- `patient` -> patient-service (8000)
- `doctor` -> doctor-service (8010)
- `appointment` -> appointment-service (8020)
- `notification` -> notification-service (8030)

## Examples

- `GET /api/patient/users/1`
- `POST /api/appointment/appointments`
- `GET /api/doctor/api/doctors`
- `POST /api/notification/notifications/appointment/reminder`

## Run

From repository root:

```bash
docker compose up -d --build api-gateway
```
