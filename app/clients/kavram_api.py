import requests
from flask import current_app


def _base():
    return current_app.config["KAVRAM_API_BASE_URL"]


def get_unites():
    """Tüm üniteleri döndürür."""
    resp = requests.get(f"{_base()}/unites")
    resp.raise_for_status()
    return resp.json()


def get_konular(unite_id):
    """Üniteye ait konuları döndürür."""
    resp = requests.get(f"{_base()}/unites/{unite_id}/konular")
    resp.raise_for_status()
    return resp.json()


def get_kavramlar(konu_id):
    """Konuya ait kavramları döndürür."""
    resp = requests.get(f"{_base()}/konular/{konu_id}/kavramlar")
    resp.raise_for_status()
    return resp.json()


def get_kavram(kavram_id):
    """Tek kavram detayını döndürür."""
    resp = requests.get(f"{_base()}/kavramlar/{kavram_id}")
    resp.raise_for_status()
    return resp.json()


def get_random_kavramlar(unite_id, limit=10):
    """Ön test için rastgele kavramlar döndürür."""
    resp = requests.get(f"{_base()}/kavramlar/random", params={"unite": unite_id, "limit": limit})
    resp.raise_for_status()
    return resp.json()
