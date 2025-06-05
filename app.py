from flask import Flask, jsonify, Response, request
import threading
import requests
from twilio.rest import Client
import os

app = Flask(__name__)

# 🔐 Variables de entorno desde Railway
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("VOICE_ID")
DOMAIN_URL = os.getenv("DOMAIN_URL")

# 🎙 Texto que dirá la voz Miguel
TEXTO_VOZ = """
Hola, ¿qué tal? ¿Hablo con [nombre]? Mucho gusto, soy Miguel, asesor de ventas de BPS E-TRUCK.
Me contacto contigo porque recibimos el interés de tu parte para ser distribuidor de la marca.
¿Te encuentro ocupado o tienes unos minutos para hablar?
"""

# 🔊 Función que lanza la llamada completa
def iniciar_llamada(lead_phone_number):
    try:
        print("[INFO] Generando audio con ElevenLabs...")
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": TEXTO_VOZ,
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.9
                }
            }
        )

        if response.status_code != 200:
            print(f"[ERROR] ElevenLabs: {response.text}")
            return

        # Guardar audio en static/
        audio_path = "static/voz_llamada.mp3"
        with open(audio_path, "wb") as f:
            f.write(response.content)

        print("[INFO] Audio guardado como voz_llamada.mp3")

        # Llamar al lead con Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twiml_url = f"{DOMAIN_URL}/twiml-bps"

        print(f"[INFO] Llamando a {lead_phone_number}...")
        call = client.calls.create(
            to=lead_phone_number,
            from_=TWILIO_PHONE_NUMBER,
            url=twiml_url
        )

        print(f"[INFO] Llamada iniciada. SID: {call.sid}")

    except Exception as e:
        print(f"[ERROR EN LLAMADA]: {e}")

# Endpoint público para iniciar llamada (ej: /probar-llamada?telefono=+5218180000000)
@app.route("/probar-llamada", methods=["GET"])
def probar_llamada():
    telefono = request.args.get("telefono")
    if not telefono:
        return jsonify({"error": "Falta el número del prospecto. Usa ?telefono=+521..."})

    hilo = threading.Thread(target=iniciar_llamada, args=(telefono,))
    hilo.start()
    return jsonify({"status": f"Llamada iniciada al número {telefono}"}), 200

# Endpoint para Twilio: reproduce el audio
@app.route("/twiml-bps", methods=["GET", "POST"])
def twiml_bps():
    twiml = f"""
    <Response>
        <Play>{DOMAIN_URL}/static/voz_llamada.mp3</Play>
    </Response>
    """
    return Response(twiml, mimetype="text/xml")

# Dev server (opcional local)
if __name__ == "__main__":
    app.run(debug=True)

