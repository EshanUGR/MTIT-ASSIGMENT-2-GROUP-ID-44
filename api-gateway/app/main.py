import json
from datetime import date, time
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from app.config import settings

app = FastAPI(title="API Gateway", version="1.0.0")
bearer_scheme = HTTPBearer()

SERVICES = {
    "patient": settings.PATIENT_SERVICE_URL,
    "doctor": settings.DOCTOR_SERVICE_URL,
    "appointment": settings.APPOINTMENT_SERVICE_URL,
    "notification": settings.NOTIFICATION_SERVICE_URL,
}

SERVICE_PATH_PREFIXES = {
    "patient": "",
    "doctor": "/api",
    "appointment": "",
    "notification": "",
}


def _resolve_service_prefix(service: str, subpath: str) -> str:
    if service != "doctor":
        return SERVICE_PATH_PREFIXES.get(service, "")

    normalized = subpath.lstrip("/")
    if normalized.startswith("api"):
        return ""
    if normalized.startswith("doctors") or normalized == "":
        return "/api"
    return ""

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


class DoctorCreatePayload(BaseModel):
    name: str = Field(min_length=2)
    specialization: str = Field(min_length=2)
    email: str
    phone: str = Field(min_length=7, max_length=15)
    hospital: str = Field(min_length=2)


class DoctorUpdatePayload(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    specialization: str | None = Field(default=None, min_length=2)
    email: str | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=15)
    hospital: str | None = Field(default=None, min_length=2)


class AvailabilityCreatePayload(BaseModel):
    date: date
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")


class PatientCreatePayload(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    age: int
    gender: str
    address: str
    password: str = Field(min_length=8, max_length=72)


class PatientUpdatePayload(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    age: int | None = None
    gender: str | None = None
    address: str | None = None
    status: str | None = None
    is_active: bool | None = None


class PatientLoginPayload(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class AppointmentCreatePayload(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str


class NotificationTriggerPayload(BaseModel):
    appointment_id: int
    patient_id: int | None = None
    doctor_id: int | None = None
    appointment_date: str | None = None
    channel: str = "in_app"
    scheduled_for: str | None = None


def _notification_payload_for_forward(payload: NotificationTriggerPayload) -> dict[str, Any]:
    data = payload.model_dump(exclude_none=True)
    scheduled_for = data.get("scheduled_for")

    # Swagger UI commonly sends "string" as a placeholder for optional string fields.
    if isinstance(scheduled_for, str) and scheduled_for.strip().lower() in {"", "string", "null", "none"}:
        data.pop("scheduled_for", None)

    return data


async def forward_request(service: str, path: str, method: str, **kwargs) -> Any:
    """Forward request to the appropriate microservice."""
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    if method not in ALLOWED_METHODS:
        raise HTTPException(status_code=405, detail="Method not allowed")

    url = f"{SERVICES[service]}{path}" if path else SERVICES[service]

    timeout = httpx.Timeout(settings.REQUEST_TIMEOUT_SECONDS)
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.request(method=method, url=url, **kwargs)
            if not response.text:
                payload: Any = None
            else:
                try:
                    payload = response.json()
                except json.JSONDecodeError:
                    payload = {"raw": response.text}

            return JSONResponse(
                content=payload,
                status_code=response.status_code,
            )
        except httpx.TimeoutException as e:
            raise HTTPException(status_code=504, detail=f"Gateway timeout: {str(e)}") from e
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Service unavailable: {str(e)}") from e


async def _proxy(service: str, subpath: str, request: Request):
    service_prefix = _resolve_service_prefix(service, subpath)
    path_suffix = f"/{subpath}" if subpath else ""
    target_path = f"{service_prefix}{path_suffix}"
    query = request.url.query
    if query:
        target_path = f"{target_path}?{query}" if target_path else f"/?{query}"

    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }

    body = await request.body()
    payload_kwargs: dict[str, Any] = {}
    if body:
        payload_kwargs["content"] = body

    return await forward_request(
        service=service,
        path=target_path,
        method=request.method.upper(),
        headers=headers,
        **payload_kwargs,
    )


def _passthrough_headers(request: Request) -> dict[str, str]:
    return {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length"}
    }


def _auth_headers(credentials: HTTPAuthorizationCredentials) -> dict[str, str]:
    return {"Authorization": f"Bearer {credentials.credentials}"}


@app.get("/")
def read_root():
    return {
        "message": "API Gateway is running",
        "available_services": list(SERVICES.keys()),
    }


@app.get("/health")
def health():
    return {"service": "api-gateway", "status": "ok"}


@app.get("/services")
def list_services():
    return {"services": list(SERVICES.keys())}


# Swagger-friendly doctor routes
@app.post("/gateway/doctor/doctors")
async def create_doctor(payload: DoctorCreatePayload):
    return await forward_request(
        "doctor",
        "/api/doctors",
        "POST",
        json=payload.model_dump(by_alias=True),
    )


@app.get("/gateway/doctor/doctors")
async def get_all_doctors():
    return await forward_request("doctor", "/api/doctors", "GET")


@app.get("/gateway/doctor/doctors/available")
async def get_available_doctors(
    date_value: date = Query(alias="date"),
    start_time: time | None = Query(default=None, alias="startTime"),
    end_time: time | None = Query(default=None, alias="endTime"),
):
    query_parts = [f"date={date_value.isoformat()}"]
    if start_time is not None:
        query_parts.append(f"startTime={start_time.isoformat()}")
    if end_time is not None:
        query_parts.append(f"endTime={end_time.isoformat()}")
    query = "&".join(query_parts)
    return await forward_request("doctor", f"/api/doctors/available?{query}", "GET")


@app.get("/gateway/doctor/doctors/{doctor_id}")
async def get_doctor_by_id(doctor_id: int):
    return await forward_request("doctor", f"/api/doctors/{doctor_id}", "GET")


@app.put("/gateway/doctor/doctors/{doctor_id}")
async def update_doctor(doctor_id: int, payload: DoctorUpdatePayload):
    return await forward_request(
        "doctor",
        f"/api/doctors/{doctor_id}",
        "PUT",
        json=payload.model_dump(exclude_unset=True, by_alias=True),
    )


@app.delete("/gateway/doctor/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int):
    return await forward_request("doctor", f"/api/doctors/{doctor_id}", "DELETE")


@app.post("/gateway/doctor/doctors/{doctor_id}/availability")
async def add_doctor_availability(doctor_id: int, payload: AvailabilityCreatePayload):
    return await forward_request(
        "doctor",
        f"/api/doctors/{doctor_id}/availability",
        "POST",
        json=payload.model_dump(by_alias=True),
    )


# Swagger-friendly patient routes
@app.post("/gateway/patient/users")
async def register_patient(payload: PatientCreatePayload):
    return await forward_request(
        "patient",
        "/users/",
        "POST",
        json=payload.model_dump(),
    )


@app.post("/gateway/patient/users/login")
async def login_patient(payload: PatientLoginPayload):
    return await forward_request(
        "patient",
        "/users/login",
        "POST",
        json=payload.model_dump(),
    )


@app.get("/gateway/patient/users")
async def get_all_patients(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    headers = _passthrough_headers(request)
    headers.update(_auth_headers(credentials))
    return await forward_request(
        "patient",
        "/users/",
        "GET",
        headers=headers,
    )


@app.get("/gateway/patient/users/me")
async def get_my_profile(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    headers = _passthrough_headers(request)
    headers.update(_auth_headers(credentials))
    return await forward_request(
        "patient",
        "/users/me",
        "GET",
        headers=headers,
    )


@app.get("/gateway/patient/users/{user_id}")
async def get_patient_by_id(
    user_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    headers = _passthrough_headers(request)
    headers.update(_auth_headers(credentials))
    return await forward_request(
        "patient",
        f"/users/{user_id}",
        "GET",
        headers=headers,
    )


@app.put("/gateway/patient/users/{user_id}")
async def update_patient(user_id: int, payload: PatientUpdatePayload):
    return await forward_request(
        "patient",
        f"/users/{user_id}",
        "PUT",
        json=payload.model_dump(exclude_unset=True),
    )


@app.patch("/gateway/patient/users/{user_id}/deactivate")
async def deactivate_patient(
    user_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    headers = _passthrough_headers(request)
    headers.update(_auth_headers(credentials))
    return await forward_request(
        "patient",
        f"/users/{user_id}/deactivate",
        "PATCH",
        headers=headers,
    )


@app.delete("/gateway/patient/users/{user_id}")
async def delete_patient(
    user_id: int,
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    headers = _passthrough_headers(request)
    headers.update(_auth_headers(credentials))
    return await forward_request(
        "patient",
        f"/users/{user_id}",
        "DELETE",
        headers=headers,
    )


# Swagger-friendly appointment routes
@app.post("/gateway/appointment/appointments")
async def create_appointment(payload: AppointmentCreatePayload):
    return await forward_request(
        "appointment",
        "/appointments",
        "POST",
        json=payload.model_dump(),
    )


@app.get("/gateway/appointment/appointments/by-id/{appointment_id}")
async def get_appointment_by_id(appointment_id: int):
    return await forward_request(
        "appointment",
        f"/appointments/by-id/{appointment_id}",
        "GET",
    )


@app.get("/gateway/appointment/appointments/{user_id}")
async def get_user_appointments(user_id: int):
    return await forward_request(
        "appointment",
        f"/appointments/{user_id}",
        "GET",
    )


@app.delete("/gateway/appointment/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int):
    return await forward_request(
        "appointment",
        f"/appointments/{appointment_id}",
        "DELETE",
    )


# Swagger-friendly notification routes
@app.post("/gateway/notification/notifications/appointment/confirmation")
async def send_appointment_confirmation(payload: NotificationTriggerPayload):
    return await forward_request(
        "notification",
        "/notifications/appointment/confirmation",
        "POST",
        json=_notification_payload_for_forward(payload),
    )


@app.post("/gateway/notification/notifications/appointment/reminder")
async def send_appointment_reminder(payload: NotificationTriggerPayload):
    return await forward_request(
        "notification",
        "/notifications/appointment/reminder",
        "POST",
        json=_notification_payload_for_forward(payload),
    )


@app.post("/gateway/notification/notifications/appointment/cancellation")
async def send_appointment_cancellation(payload: NotificationTriggerPayload):
    return await forward_request(
        "notification",
        "/notifications/appointment/cancellation",
        "POST",
        json=_notification_payload_for_forward(payload),
    )


@app.get("/gateway/notification/notifications/patient/{patient_id}")
async def get_notifications_for_patient(patient_id: int):
    return await forward_request(
        "notification",
        f"/notifications/patient/{patient_id}",
        "GET",
    )


@app.get("/gateway/notification/notifications/appointment/{appointment_id}")
async def get_notifications_for_appointment(appointment_id: int):
    return await forward_request(
        "notification",
        f"/notifications/appointment/{appointment_id}",
        "GET",
    )


@app.api_route("/gateway/patient", methods=list(ALLOWED_METHODS), include_in_schema=False)
@app.api_route("/gateway/patient/{path:path}", methods=list(ALLOWED_METHODS), include_in_schema=False)
async def patient_gateway(request: Request, path: str = ""):
    return await _proxy("patient", path, request)


@app.api_route("/gateway/doctor", methods=list(ALLOWED_METHODS), include_in_schema=False)
@app.api_route("/gateway/doctor/{path:path}", methods=list(ALLOWED_METHODS), include_in_schema=False)
async def doctor_gateway(request: Request, path: str = ""):
    return await _proxy("doctor", path, request)


@app.api_route("/gateway/appointment", methods=list(ALLOWED_METHODS), include_in_schema=False)
@app.api_route("/gateway/appointment/{path:path}", methods=list(ALLOWED_METHODS), include_in_schema=False)
async def appointment_gateway(request: Request, path: str = ""):
    return await _proxy("appointment", path, request)


@app.api_route("/gateway/notification", methods=list(ALLOWED_METHODS), include_in_schema=False)
@app.api_route("/gateway/notification/{path:path}", methods=list(ALLOWED_METHODS), include_in_schema=False)
async def notification_gateway(request: Request, path: str = ""):
    return await _proxy("notification", path, request)


# Backward-compatible aliases for existing /api/* gateway routes.
@app.api_route("/api/{service}", methods=list(ALLOWED_METHODS), include_in_schema=False)
@app.api_route("/api/{service}/{path:path}", methods=list(ALLOWED_METHODS), include_in_schema=False)
async def generic_gateway(service: str, request: Request, path: str = ""):
    return await _proxy(service, path, request)
