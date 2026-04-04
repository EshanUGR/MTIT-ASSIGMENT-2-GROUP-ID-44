from fastapi import HTTPException, Request, Response
import httpx

from app.config import settings

SERVICE_URLS = {
    "patient": settings.PATIENT_SERVICE_URL,
    "doctor": settings.DOCTOR_SERVICE_URL,
    "appointment": settings.APPOINTMENT_SERVICE_URL,
    "notification": settings.NOTIFICATION_SERVICE_URL,
}

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
}


def _filter_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in headers.items()
        if key.lower() not in HOP_BY_HOP_HEADERS
    }


async def forward_request(service: str, path: str, request: Request) -> Response:
    target_base_url = SERVICE_URLS.get(service)
    if not target_base_url:
        raise HTTPException(status_code=404, detail=f"Unknown service '{service}'")

    query = request.url.query
    target_url = f"{target_base_url}/{path}" if path else target_base_url
    if query:
        target_url = f"{target_url}?{query}"

    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            outgoing_headers = _filter_headers(dict(request.headers.items()))
            payload = await request.body()

            backend_response = await client.request(
                method=request.method,
                url=target_url,
                content=payload,
                headers=outgoing_headers,
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Gateway timeout calling {service} service")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Gateway failed to reach {service} service: {exc}")

    response_headers = _filter_headers(dict(backend_response.headers.items()))
    return Response(
        content=backend_response.content,
        status_code=backend_response.status_code,
        headers=response_headers,
        media_type=backend_response.headers.get("content-type"),
    )
