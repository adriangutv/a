from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime
import os
import json

def agendar_google_meet(nombre, correo, fecha_iso):
    try:
        creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        service = build("calendar", "v3", credentials=creds)

        hora_inicio = datetime.datetime.fromisoformat(fecha_iso)
        hora_fin = hora_inicio + datetime.timedelta(minutes=30)

        evento = {
            "summary": f"Reunión con {nombre} – BPS E-TRUCK",
            "description": "Reunión automática generada por IA para distribuidor BPS.",
            "start": {
                "dateTime": hora_inicio.isoformat(),
                "timeZone": "America/Mexico_City",
            },
            "end": {
                "dateTime": hora_fin.isoformat(),
                "timeZone": "America/Mexico_City",
            },
            "attendees": [{"email": correo}],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"bps-etruck-{datetime.datetime.now().timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
        }

        evento_creado = service.events().insert(
            calendarId="primary",
            body=evento,
            conferenceDataVersion=1,
            sendUpdates="all"
        ).execute()

        return {
            "status": "success",
            "event_id": evento_creado["id"],
            "meet_link": evento_creado["hangoutLink"],
            "start": evento_creado["start"]["dateTime"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

