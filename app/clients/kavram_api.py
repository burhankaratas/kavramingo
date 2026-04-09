"""
PHP Kavram API istemcisi.
KAVRAM_API_MOCK=true  → mock_data.py'den veri döner (PHP API gerekmez)
KAVRAM_API_MOCK=false → gerçek HTTP isteği atar
"""
import os
import requests
from flask import current_app
from app.clients.mock_data import (
    mock_get_unites,
    mock_get_konular,
    mock_get_kavramlar,
    mock_get_kavram,
    mock_get_random_kavramlar,
)


def _is_mock():
    return os.getenv("KAVRAM_API_MOCK", "false").lower() == "true"


def _base():
    return current_app.config["KAVRAM_API_BASE_URL"]


def _headers():
    token = current_app.config.get("KAVRAM_API_TOKEN", "")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _unwrap(payload):
    if isinstance(payload, dict) and "data" in payload and "current_page" in payload:
        return payload.get("data", [])
    return payload


def get_unites():
    """Tüm üniteleri döndürür."""
    if _is_mock():
        return mock_get_unites()
    try:
        resp = requests.get(f"{_base()}/api/v1/unites", headers=_headers(), timeout=7)
        resp.raise_for_status()
        return _unwrap(resp.json())
    except requests.exceptions.RequestException:
        return []


def get_konular(unite_id):
    """Üniteye ait konuları döndürür."""
    if _is_mock():
        return mock_get_konular(int(unite_id))
    try:
        resp = requests.get(f"{_base()}/api/v1/unites/{unite_id}/konular", headers=_headers(), timeout=7)
        resp.raise_for_status()
        return _unwrap(resp.json())
    except requests.exceptions.RequestException:
        return []


def get_unite(unite_id):
    if _is_mock():
        for u in mock_get_unites():
            if int(u.get("id", 0)) == int(unite_id):
                return u
        return None
    try:
        resp = requests.get(f"{_base()}/api/v1/unites/{unite_id}", headers=_headers(), timeout=7)
        resp.raise_for_status()
        payload = resp.json()
        return payload if isinstance(payload, dict) else None
    except requests.exceptions.RequestException:
        return None


def get_kavramlar(konu_id):
    """Konuya ait kavramları döndürür."""
    if _is_mock():
        return mock_get_kavramlar(int(konu_id))
    try:
        resp = requests.get(f"{_base()}/api/v1/konular/{konu_id}/kavramlar", headers=_headers(), timeout=7)
        resp.raise_for_status()
        return _unwrap(resp.json())
    except requests.exceptions.RequestException:
        return []


def get_kavram(kavram_id):
    """Tek kavram detayını döndürür."""
    if _is_mock():
        return mock_get_kavram(int(kavram_id))
    try:
        resp = requests.get(f"{_base()}/kavramlar/{kavram_id}", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return None


def get_random_kavramlar(unite_id, limit=10):
    """Ön test için API placement feed döndürür."""
    if _is_mock():
        return mock_get_random_kavramlar(int(unite_id), int(limit))
    try:
        resp = requests.get(
            f"{_base()}/api/v1/placement-feed",
            params={"grade": unite_id},
            headers=_headers(),
            timeout=7,
        )
        resp.raise_for_status()
        payload = resp.json()
        items = payload.get("items", []) if isinstance(payload, dict) else []
        out = []
        for i, item in enumerate(items, start=1):
            q = item.get("question", {})
            choices = q.get("choices", {})
            out.append({
                "id": q.get("id", i),
                "topic": q.get("topic_name", "Konu"),
                "question": q.get("prompt", ""),
                "choices": [choices.get("A", ""), choices.get("B", ""), choices.get("C", ""), choices.get("D", "")],
                "correct": choices.get(q.get("correct_choice", "A"), ""),
                "unit_id": item.get("unit", {}).get("id"),
            })
        return out
    except requests.exceptions.RequestException:
        return []


def get_placement_feed(grade):
    if _is_mock():
        return []
    try:
        resp = requests.get(
            f"{_base()}/api/v1/placement-feed",
            params={"grade": grade},
            headers=_headers(),
            timeout=7,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return {"items": []}


def get_quiz_feed(grade, unit_id, quiz_type):
    if _is_mock():
        return {"questions": []}
    try:
        resp = requests.get(
            f"{_base()}/api/v1/quiz-feed",
            params={"grade": grade, "unit_id": unit_id, "quiz_type": quiz_type},
            headers=_headers(),
            timeout=7,
        )
        resp.raise_for_status()
        payload = resp.json()
        return payload if isinstance(payload, dict) else {"questions": []}
    except requests.exceptions.RequestException:
        return {"questions": []}
