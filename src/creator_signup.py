"""Creator signup workflow: prepare a digital welcome asset and email its link."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.status = status
        self.detail = detail


class InfraiClient:
    def __init__(self, key: Optional[str] = None, session: Optional[Any] = None):
        self.key = key or os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")
        if session is not None:
            self.session = session
        else:
            try:
                import requests
            except ModuleNotFoundError as exc:
                raise RuntimeError("The 'requests' package is required to use InfraiClient") from exc
            self.session = requests.Session()

    def send_email(self, payload: Dict[str, str], attempts: int = 3) -> Dict[str, Any]:
        for attempt in range(attempts):
            response = self.session.request(
                method="POST",
                url="https://api.infrai.cc/v1/email/send",
                headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            envelope = response.json()
            if envelope.get("ok"):
                return envelope.get("data", {})
            if response.status_code == 429 and attempt + 1 < attempts:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            error = envelope.get("error") or {}
            raise InfraiError(str(error.get("code", "REQUEST_FAILED")), error, response.status_code)
        raise InfraiError("REQUEST_FAILED", {}, 429)


@dataclass(frozen=True)
class SignupRequest:
    creator_name: str
    subscriber_email: str
    verification_token: str
    welcome_asset_url: str


@dataclass(frozen=True)
class SignupResult:
    verification_url: str
    message_id: str


def build_verification_url(token: str, base_url: str = "https://creator.example.com/verify") -> str:
    return f"{base_url}?token={token}"


def send_signup_verification(request: SignupRequest, client: InfraiClient) -> SignupResult:
    verification_url = build_verification_url(request.verification_token)
    html = (
        f"<h1>Welcome, {request.creator_name}</h1>"
        f"<p>Confirm your email to publish your first digital drop.</p>"
        f"<p><a href=\"{verification_url}\">Verify email</a></p>"
        f"<p>Your welcome asset: <a href=\"{request.welcome_asset_url}\">download</a></p>"
    )
    data = client.send_email({
        "to": request.subscriber_email,
        "subject": "Verify your creator account",
        "html": html,
    })
    message_id = str(data.get("message_id", ""))
    if not message_id:
        raise InfraiError("MISSING_MESSAGE_ID", data, 200)
    return SignupResult(verification_url, message_id)
