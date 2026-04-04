# Notification Service

FastAPI microservice for healthcare appointment notifications.

## Responsibilities

- Appointment confirmation notifications
- Appointment reminder notifications
- Appointment cancellation notifications
- Notification history queries by patient or appointment

## Run with Docker Compose

From the repository root:

```bash
docker compose up -d --build
```

Service URL:

- http://localhost:8030

## API Endpoints

### Health

- `GET /health`

### Trigger notifications

- `POST /notifications/appointment/confirmation`
- `POST /notifications/appointment/reminder`
- `POST /notifications/appointment/cancellation`

Payload:

```json
{
  "appointment_id": 1,
  "channel": "in_app",
  "scheduled_for": null
}
```

### Query notifications

- `GET /notifications/patient/{patient_id}`
- `GET /notifications/appointment/{appointment_id}`

## Integration points

- Fetches appointment details from appointment-service endpoint:
  - `GET /appointments/by-id/{appointment_id}`

## Environment Variables

- `PORT` (default: `8030`)
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `APPOINTMENT_SERVICE_URL`
- `PATIENT_SERVICE_URL`
- `DOCTOR_SERVICE_URL`
