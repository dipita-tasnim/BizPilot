BizPilot Backend (Django)

Setup (Windows PowerShell)

1) Create and activate venv

```
python -m venv venv
./venv/Scripts/Activate.ps1
```

2) Install dependencies

```
pip install -r server/requirements.txt
```

3) Initialize DB and run server

```
cd server
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

API

- POST http://localhost:8000/api/chat/
- Body: { "message": "..." }
- Returns canned response matching the three example intents; otherwise a default reply.

Note: CORS is open for local development.

