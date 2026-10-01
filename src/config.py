from __future__ import annotations

import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CIRCUIT_DIR = DATA_DIR / "circuits"
MODEL_DIR = ROOT / "models"

for _d in (RAW_DIR, PROCESSED_DIR, CIRCUIT_DIR, MODEL_DIR):
    _d.mkdir(parents=True, exist_ok=True)

FIRST_SEASON = 1996
CURRENT_SEASON = int(os.environ.get("F1_SEASON") or date.today().year)

API_BASE = "https://api.jolpi.ca/ergast/f1"
API_PAGE_SIZE = 100
API_SLEEP = 0.30

CIRCUIT_GEO_BASE = "https://raw.githubusercontent.com/bacinger/f1-circuits/master"

PODIUM_CUTOFF = 3

RECENCY_HALF_LIFE_YEARS = 8.0

FORM_DECAY_PER_RACE = 0.93
TRACK_DECAY_PER_YEAR = 0.75

VALIDATION_SEASONS = list(range(2014, CURRENT_SEASON + 1))
MIN_TRAIN_SEASONS = 8

RANDOM_STATE = 42

SITE_URL = (os.environ.get("F1_SITE_URL") or "https://f1racepredictor.com").rstrip("/")
SITE_NAME = "Race Predictor"
LANGUAGES = ("en", "pl", "de", "es", "fr", "it", "nl", "pt")

LEGAL = {
    "operator": os.environ.get("F1_OPERATOR_NAME") or "[OPERATOR NAME]",
    "address": os.environ.get("F1_OPERATOR_ADDRESS") or "[OPERATOR ADDRESS]",
    "email": os.environ.get("F1_CONTACT_EMAIL") or "[CONTACT EMAIL]",
    "country": os.environ.get("F1_GOVERNING_COUNTRY") or "[COUNTRY]",
    "hosting": os.environ.get("F1_HOSTING_PROVIDER") or "[HOSTING PROVIDER]",
    "log_days": os.environ.get("F1_LOG_RETENTION_DAYS") or "30",
    "updated": os.environ.get("F1_LEGAL_UPDATED") or "2026-10-01",
}
