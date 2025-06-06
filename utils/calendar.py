kimport os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def agendar_google_meet(nombre, correo, fecha_iso):
    try:
        # Leer credenciales desde variable de entorno
        creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        # Construir servicio de Google Calendar
        service = build("calendar", "v3", credentials=creds)

        # Parsear fechas
        hora_inicio = datetime.datetime.fromisoformat(fecha_iso)
        hora_fin = hora_inicio + datetime.timedelta(minutes=30)

        # Construir evento
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
                    "requestId": f"bps-{int(datetime.datetime.now().timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
        }

        # Leer ID del calendario desde variable de entorno
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
        if not calendar_id:
            return {"status": "error", "message": "Falta GOOGLE_CALENDAR_ID"}

        # Insertar evento
        evento_creado = service.events().insert(
            calendarId=calendar_id,
            body=evento,
            conferenceDataVersion=1,
            sendUpdates="all"
        ).execute()

        return {
            "status": "success",
            "event_id": evento_creado["id"],
            "meet_link": evento_creado.get("hangoutLink", ""),
            "start": evento_creado["start"]["dateTime"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

