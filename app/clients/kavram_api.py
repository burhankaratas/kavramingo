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


def get_unites():
    """Tüm üniteleri döndürür."""
    if _is_mock():
        return mock_get_unites()
    try:
        resp = requests.get(f"{_base()}/unites", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return []


def get_konular(unite_id):
    """Üniteye ait konuları döndürür."""
    if _is_mock():
        return mock_get_konular(int(unite_id))
    try:
        resp = requests.get(f"{_base()}/unites/{unite_id}/konular", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return []


def get_kavramlar(konu_id):
    """Konuya ait kavramları döndürür."""
    if _is_mock():
        return mock_get_kavramlar(int(konu_id))
    try:
        resp = requests.get(f"{_base()}/konular/{konu_id}/kavramlar", timeout=5)
        resp.raise_for_status()
        return resp.json()
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
    """Ön test için rastgele kavramlar döndürür."""
    if _is_mock():
        return mock_get_random_kavramlar(int(unite_id), int(limit))
    try:
        resp = requests.get(
            f"{_base()}/kavramlar/random",
            params={"unite": unite_id, "limit": limit},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException:
        return []
