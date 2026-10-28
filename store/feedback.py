import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class FeedbackNotSent(Exception):
    pass


def send_feedback(data):
    """Forward a validated FeedbackForm's cleaned data to the feedback backend."""
    if not settings.FEEDBACK_PROJECT_ID:
        raise FeedbackNotSent("FEEDBACK_PROJECT_ID is not set")

    payload = {
        "projectId": settings.FEEDBACK_PROJECT_ID,
        "projectName": settings.FEEDBACK_PROJECT_NAME,
        "category": data["category"],
        "message": data["message"],
        "metadata": {
            "pageUrl": data.get("page_url") or None,
            "browser": data.get("browser") or None,
        },
    }
    if data.get("name") or data.get("email"):
        payload["user"] = {"name": data.get("name") or None, "email": data.get("email") or None}
    if data.get("viewport_width") and data.get("viewport_height"):
        payload["metadata"]["viewport"] = {
            "width": data["viewport_width"],
            "height": data["viewport_height"],
        }

    try:
        response = requests.post(
            f"{settings.FEEDBACK_API_URL}/feedback/submit",
            files={"feedback": (None, json.dumps(payload), "application/json")},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise FeedbackNotSent(f"Feedback backend unreachable: {exc}") from exc

    if response.status_code != 201:
        logger.warning("Feedback backend returned %s: %s", response.status_code, response.text[:500])
        raise FeedbackNotSent(f"Feedback backend returned {response.status_code}")
