from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://api.smakmail.com/api/v1"


@dataclass
class SmakMailAPIError(RuntimeError):
    status: int | None
    message: str
    payload: Any = None
    retry_after: str | None = None

    def __str__(self) -> str:
        prefix = f"HTTP {self.status}: " if self.status is not None else ""
        return prefix + self.message


class SmakMailClient:
    """Minimal client for SmakMail receive-only mailbox API reads."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        api_key = api_key.strip()
        if not api_key:
            raise ValueError("api_key must not be empty")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def me(self) -> Any:
        return self._get("/me")

    def mailbox_messages(
        self,
        email: str,
        *,
        mailbox_password: str | None = None,
    ) -> Any:
        return self._get(
            "/mailbox/messages",
            params={"email": email},
            mailbox_password=mailbox_password,
        )

    def mailbox_latest_code(
        self,
        email: str,
        *,
        mailbox_password: str | None = None,
    ) -> Any:
        return self._get(
            "/mailbox/latest-code",
            params={"email": email},
            mailbox_password=mailbox_password,
        )

    def _get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        mailbox_password: str | None = None,
    ) -> Any:
        query = f"?{urlencode(params)}" if params else ""
        url = f"{self.base_url}{path}{query}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "smakmail-python-client/0.1.0",
        }
        if mailbox_password is not None:
            headers["X-Mailbox-Password"] = mailbox_password

        request = Request(url, headers=headers, method="GET")

        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return None
                return json.loads(body)
        except HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                payload = raw or None

            message = "SmakMail API request failed"
            if isinstance(payload, dict):
                candidate = payload.get("error") or payload.get("message")
                if isinstance(candidate, str) and candidate:
                    message = candidate

            raise SmakMailAPIError(
                status=exc.code,
                message=message,
                payload=payload,
                retry_after=exc.headers.get("Retry-After"),
            ) from exc
        except URLError as exc:
            raise SmakMailAPIError(
                status=None,
                message=f"Network error: {exc.reason}",
            ) from exc
