import os
from twilio.rest import Client

def llamar_a_usuario(numero_destino: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
    domain_url = os.getenv("DOMAIN_URL")  # ejemplo: https://web-production-xxxx.up.railway.app

    if not all([account_sid, auth_token, twilio_number, domain_url]):
        print("⚠️ Faltan variables de entorno para Twilio.")
        return False

    client = Client(account_sid, auth_token)

    try:
        llamada = client.calls.create(
            to=numero_destino,
            from_=twilio_number,
            url=f"{domain_url}/twiml-bps"  # Aquí se sirve el XML con la voz generada
        )
        print(f"✅ Llamada iniciada con SID: {llamada.sid}")
        return True
    except Exception as e:
        print(f"❌ Error al iniciar la llamada: {e}")
        return False

