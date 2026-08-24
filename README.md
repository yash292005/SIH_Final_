# SkyGuard Weather — Django

A runnable Django weather dashboard using Open-Meteo Weather + Geocoding APIs and Open-Meteo's GloFAS-based Flood API.

## Run

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open running on local host not deployed yet


Search any city, e.g. Kolkata, Delhi, Mumbai, London.

## Important

The flood value is a demo risk indicator, not an official flood warning. For production flood alerts, use official hydrological thresholds and government warning sources.
